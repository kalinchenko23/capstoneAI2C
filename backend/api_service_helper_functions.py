from fastapi import FastAPI, Query, Body, HTTPException
from llm_service import get_review_summary
from vlm_service import get_safe_prompt, generate_summary, analyze_image
from deep_translator import GoogleTranslator
from datetime import datetime
import httpx
import aiohttp
import json
import base64

async def getting_street_view_image(
    location: str,
    key: str):
    """
    Fetches a Street View image from the Google Street View API and encodes it for VLM processing.

    Args:
        location (str): The location for the Street View image. Can be an address or latitude/longitude.
        key (str): The API key for authenticating with the Google Street View API.

    Returns:
        tuple: (Image URI, Encoded Image)
    """

    if not location:
        raise HTTPException(
            status_code=400,
            detail="You must provide a 'location' or parameter."
        )
    
    # Build query parameters
    params = {
        "size": "600x400",
        "key": key
    }
    
    params["location"] = location
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://maps.googleapis.com/maps/api/streetview?{query}"

    # Gets and Base64 encodes the imagae
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        encoded_string = base64.b64encode(response.content).decode('utf-8')

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch the image: {response.text}"
        ) 
    return (str(response.url),encoded_string)



async def get_photo(name: str,api_key):
    """
    Get and encode an image from the provided photo URI.

    Returns:
         str: Base64 encoded string.
    """

    # Validate input
    if not name:
        raise ValueError("The 'name' parameter cannot be empty.")

    url = f"https://places.googleapis.com/v1/{name}/media?key={api_key}&maxWidthPx={800}&maxHeightPx={600}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                
                #Base64 encode image
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                return encoded_image
            else:
                return None
  


async def response_formatter(responce,api_key,prompt_info,tiers,llm_key,vlm_key):
    """
    Extracts specific fields from a JSON response provided by GoogleAPI and formats them into a structured list of dictionaries.

    Args:
        response (dict): The Google API JSON response containing place details.

    Returns:
        list: A list of formatted dictionaries containing relevant place information.
    """
    result=[] 
    
    #Generating prompt for VLM
    try:
        vlm_prompt=get_safe_prompt(prompt_info, vlm_key)
    except Exception as ex:
        raise HTTPException(status_code=401,detail=f"{ex}")

    for place in responce:
        new_data={}
        try: 
            new_data["name"]={}
            new_data["name"]["original_name"]=place["displayName"]["text"]
            new_data["name"]["translated_name"]= GoogleTranslator(source="auto",target='en').translate(place["displayName"]["text"])
        except KeyError as ex:
            new_data["name"]="Name is not provided"
        try:
            new_data["type"]=place["types"][0]
        except KeyError as ex:
            new_data["type"]="Type is not provided"
        try:
            new_data["website"]=place["websiteUri"]
        except KeyError as ex:
            new_data["website"]="Website is not provided"
        try:
            new_data["google_maps_url"]=place["googleMapsUri"]
        except KeyError as ex:
            new_data["google_maps_url"]="Google maps url is not provided"    
        try:
            new_data["phone_number"]=place["nationalPhoneNumber"]
        except KeyError as ex:
            new_data["phone_number"]="Phone number is not provided"
        try:
            new_data["address"]=place["formattedAddress"]
        except KeyError as ex:
            new_data["address"]="Address number is not provided"
        try:
            new_data["latitude"]=place["location"]["latitude"]
            new_data["longitude"]=place["location"]["longitude"]
        except KeyError as ex:
            new_data["latitude"]="Latitude is not provided"
            new_data["longitude"]="Longitude is not provided"
            
        if "reviews" in tiers:
            try:
                #Calling LLM summarization function
                new_data["reviews_summary"] = get_review_summary(llm_key,place["reviews"])
                new_data["reviews"] = []
                ratings=[]
                times=[]
                for review in place["reviews"]:
                    #appends review link and origianl language
                    r={}
                    r["author_name"]={}
                    r["review_url"]=review["googleMapsUri"]
                    r["text"]=review["text"]["text"]
                    r["original_text"]=review["originalText"]["text"]
                    r["original_language"]=review["originalText"]["languageCode"]
                    r["author_name"]["original_name"]=review["authorAttribution"]["displayName"]
                    r["author_name"]["translated_name"]= GoogleTranslator(source="auto",target='en').translate(review["authorAttribution"]["displayName"])
                    r["author_url"]=review["authorAttribution"]["uri"]
                    r["publish_date"]=review["relativePublishTimeDescription"]
                    r["rating"]=review["rating"]
                    new_data["reviews"].append(r)
                    
                    ratings.append(review["rating"])
                    times.append(review["publishTime"])
                
                #Calculates average reviews value
                average = sum(ratings) / len(ratings)
                new_data["rating"]=f"average: {average} out of {len(ratings)} reviews"

                #Calculates average time span
                timestamp_objects = [datetime.fromisoformat(ts[:26]).date() for ts in times]
                latest_date = max(timestamp_objects)
                most_recent_date = min(timestamp_objects)
                date_diff = latest_date - most_recent_date
                new_data["reviews_span"]=f"latest date: {latest_date}, most recent date: {most_recent_date}, date difference: {date_diff.days} days"
            except ValueError as ex:
                new_data["reviews_span"]="Error retreiving timestamp"
            except KeyError as ex:
                new_data["reviews"]="Reviews are not provided"

        if "photos" in tiers:
            try:
                new_data["url_to_all_photos"]=place["photos"][0]["googleMapsUri"]
                new_data["photos"] = []
                
                for photo in place["photos"]:
                    photo_info={}
                    #Retreiving photos
                    encoded_photo=await get_photo(photo["name"],api_key)
                    #Sending photos to VLM for the insight
                    vlm_insight=await analyze_image(encoded_photo,vlm_prompt,vlm_key)
                    photo_info["vlm_insight"]=vlm_insight
                    photo_info["url"]=photo["googleMapsUri"]
                    new_data["photos"].append(photo_info)
                
                new_data["prompt_used"]=vlm_prompt
                new_data["photos_summary"] = await generate_summary(new_data["photos"],vlm_key)

            except KeyError as ex:
                new_data["photos"]="Photos are not provided"
            except Exception as ex:
                raise HTTPException(status_code=int(ex.code),detail=f"{ex}")
            
            #Getting streetview image
            try:
                encoded_street_view_image = await getting_street_view_image(location,api_key)
                street_view_info={}
                street_view_info["vlm_insight"]=await analyze_image(encoded_street_view_image[1],vlm_prompt)
                street_view_info["url"]= "URL contains api key, can't be exposed" #encoded_street_view_image[0]
                new_data["street_view"]=street_view_info
            except Exception as ex:
                new_data["street_view"]="Street view is not provided"
        
        location=place["formattedAddress"]
        
        try:
            new_data["working_hours"]=place["regularOpeningHours"]["weekdayDescriptions"]
        except KeyError as ex:
            new_data["working_hours"]="Working hours are not provided"
        
        result.append(new_data)
        
    return result

