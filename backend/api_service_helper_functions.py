from fastapi import HTTPException
from datetime import datetime
from deep_translator import GoogleTranslator
from openai import AsyncOpenAI,OpenAI
from llm_service import get_review_summary
from vlm_service import get_safe_prompt, generate_summary, analyze_image
from recommender_service import rank_live_results
from logging_service import logger
import base64
import aiohttp
import httpx

# -------------------- UTILITIES --------------------

def translate(text: str) -> str:
    return GoogleTranslator(source="auto", target="en").translate(text)

def safe_get(obj: dict, keys: list, default="Not provided"):
    """Traverse nested dictionary using list of keys, return default on failure."""
    for key in keys:
        obj = obj.get(key, {})
    return obj if obj else default

# -------------------- IMAGE FUNCTIONS --------------------

async def getting_street_view_image(location: str, key: str):
    if not location:
        raise HTTPException(status_code=400, detail="You must provide a 'location' parameter.")

    params = {
        "size": "600x400",
        "key": key,
        "location": location
    }
    url = f"https://maps.googleapis.com/maps/api/streetview?" + "&".join(f"{k}={v}" for k, v in params.items())

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch the image: {response.text}")

    encoded = base64.b64encode(response.content).decode("utf-8")
    return str(response.url), encoded

async def get_photo(name: str, api_key: str) -> str | None:
    if not name:
        raise ValueError("The 'name' parameter cannot be empty.")

    url = f"https://places.googleapis.com/v1/{name}/media?key={api_key}&maxWidthPx=800&maxHeightPx=600"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return base64.b64encode(await response.read()).decode('utf-8')
            return None

# -------------------- MAIN FORMATTER --------------------

async def response_formatter(response: list, api_key: str, prompt_info: str, tiers: list, llm_key: str, vlm_key: str):
    
    result = []

    try:
        vlm_prompt = await get_safe_prompt(AsyncOpenAI(api_key=vlm_key), prompt_info)
    except Exception as ex:
        raise HTTPException(status_code=401, detail=str(ex))

    # Define llm/vlm clients
    llm_client = OpenAI(api_key=llm_key)
    vlm_client=AsyncOpenAI(api_key=vlm_key)

    for place in response:
        new_data = {
            "name": {
                "original_name": safe_get(place, ["displayName", "text"]),
                "translated_name": translate(safe_get(place, ["displayName", "text"], ""))
            },
            "type": place.get("types", ["Type is not provided"])[0],
            "website": place.get("websiteUri", "Website is not provided"),
            "google_maps_url": place.get("googleMapsUri", "Google maps url is not provided"),
            "phone_number": place.get("nationalPhoneNumber", "Phone number is not provided"),
            "address": place.get("formattedAddress", "Address is not provided"),
            "latitude": safe_get(place, ["location", "latitude"]),
            "longitude": safe_get(place, ["location", "longitude"]),
        }

        if "reviews" in tiers and place.get("reviews"):
            try:
                reviews = place["reviews"]
                new_data["reviews_summary"] = get_review_summary(llm_client, reviews)
                new_data["reviews"] = []
                ratings, times = [], []

                for r in reviews:
                    review_data = {
                        "author_name": {
                            "original_name": r["authorAttribution"]["displayName"],
                            "translated_name": translate(r["authorAttribution"]["displayName"])
                        },
                        "review_url": r.get("googleMapsUri"),
                        "text": r["text"]["text"],
                        "original_text": r["originalText"]["text"],
                        "original_language": r["originalText"]["languageCode"],
                        "author_url": r["authorAttribution"]["uri"],
                        "publish_date": r["relativePublishTimeDescription"],
                        "rating": r["rating"]
                    }
                    ratings.append(r["rating"])
                    times.append(r["publishTime"])
                    new_data["reviews"].append(review_data)

                new_data["rating"] = f"average: {sum(ratings)/len(ratings):.1f} out of {len(ratings)} reviews"

                timestamps = [datetime.fromisoformat(t[:26]).date() for t in times]
                new_data["reviews_span"] = (
                    f"latest date: {max(timestamps)}, most recent date: {min(timestamps)}, "
                    f"date difference: {(max(timestamps) - min(timestamps)).days} days"
                )
            except Exception as e:
                new_data["reviews"] = "Error parsing reviews"

        if "photos" in tiers and place.get("photos"):
            try:
                new_data["url_to_all_photos"] = place["photos"][0].get("googleMapsUri", "")
                new_data["photos"] = []

                for photo in place["photos"]:
                    encoded = await get_photo(photo["name"], api_key)
                    if not encoded:
                        continue
                    vlm_insight = await analyze_image(vlm_client,encoded, vlm_prompt)
                    new_data["photos"].append({
                        "vlm_insight": vlm_insight,
                        "url": photo["googleMapsUri"]
                    })

                new_data["prompt_used"] = vlm_prompt
                new_data["photos_summary"] = await generate_summary(vlm_client,new_data["photos"])

                # Street view image
                try:
                    loc = f"{place['location']['latitude']},{place['location']['longitude']}"
                    _, street_image = await getting_street_view_image(loc, api_key)
                    new_data["street_view"] = {
                        "vlm_insight": await analyze_image(vlm_client,street_image, vlm_prompt),
                        "url": "URL contains API key, not exposed"
                    }
                except Exception:
                    new_data["street_view"] = "Street view is not available"

            except KeyError:
                new_data["photos"] = "Photos are not available"

        new_data["working_hours"] = place.get("regularOpeningHours", {}).get("weekdayDescriptions", "Not provided")
        result.append(new_data)

        # Setting different threshhold for the ranking base of the total number of places
    if len(result)<=3:
        rank_index=rank_live_results(result, prompt_info, vlm_key, top_n=1)
    elif len(result)>=10:
        rank_index=rank_live_results(result, prompt_info, vlm_key)
    else:
        rank_index=rank_live_results(result, prompt_info, vlm_key)
    
    if rank_index:
        for i in rank_index:
            result[i[0]]["recommended"]=True
            result[i[0]]["recommendation_confidance"]=i[1]
    return result
