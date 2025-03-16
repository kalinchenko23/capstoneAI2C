from fastapi import FastAPI, Query, Body, HTTPException, Response
from user_credentials_service import authenticate
from api_service_helper_functions import getting_street_view_image, response_formatter
from typing import Optional
import httpx
import json
import re

# Load the JSON secrets config
with open("secrets.json") as config_file:
    config = json.load(config_file)

#Defining global variables
app = FastAPI()
API_KEY = config["GOOGLE_API_KEY"]
TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
GEOCODE_URL="https://maps.googleapis.com/maps/api/geocode/json"


@app.get("/geocode")
async def geocode(address = Body(), user_id = Body(), token: str =Body()):

    #The function first checks if the provided user credentials
    if authenticate(user_id,token):

        #Constructs the request URL and parameters for the geocoding service.
        url = GEOCODE_URL
        params = {
            "address": address,
            "key": API_KEY
        }
        
        #Makes an asynchronous HTTP GET request to the geocoding API (`GEOCODE_URL`), passing the address and API key.
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Error contacting the geocoding service")
            data = response.json()

        #If the API responds successfully, it extracts the latitude and longitude
        if data.get("status") != "OK":
            raise HTTPException(status_code=400, detail=f"Geocoding error: {data.get('status')}")

        location = data["results"][0]["geometry"]["location"]
        lat = location["lat"]
        lng = location["lng"]
        return (lat,lng)
    
    else: 
        return "Credentials are incorrect"



@app.post("/search_nearby")
async def search_nearby_places(text_query: str =Body(),
                               lat_sw: float = Body(),
                               lng_sw: float = Body(),
                               lat_ne: float = Body(),
                               lng_ne: float = Body(),
                               user_id = Body(), 
                               token: str =Body(),
                               prompt_info: str =Body(),
                               tiers: list = Body(),
                               pageToken: Optional[str] = Body(default=None),
                               fieldMask: str = Body(default="places.displayName,places.types,places.websiteUri,places.nationalPhoneNumber,places.formattedAddress,places.location,places.reviews,places.photos,places.regularOpeningHours,places.googleMapsUri,nextPageToken")):
    
    """
    This endpoint performs a text-based search for places within a specified bounding box.
    It returns places that match the given text query and includes pagination support.
    """
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": fieldMask
    }

    payload={
    "textQuery": text_query,
    "locationRestriction": {
        "rectangle": {
            "low": {
                "latitude": lat_sw,
                "longitude": lng_sw
            },
            "high": {
                "latitude": lat_ne,
                "longitude": lng_ne
            }
        }
    },
    "pageToken": pageToken
    
    }
    result={}
    if not re.match(r'^[a-zA-Z0-9 _-]+$', user_id):
        raise HTTPException(status_code=401, detail=f"user_id field contains invalid characters. Only letters, numbers, spaces, underscores, and hyphens are allowed.")
    elif not re.match(r'^[a-zA-Z0-9 _-]+$', token):
        raise HTTPException(status_code=422, detail="token field contains invalid characters. Only letters, numbers, spaces, underscores, and hyphens are allowed.")
    if authenticate(user_id,token):
        async with httpx.AsyncClient() as client:
            response = await client.post(TEXT_SEARCH_URL, json=payload, headers=headers)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from Google API: {response.text}"
            )
        
        if "places" in response.json().keys():
            result=response.json()["places"]
        else:
            return result
        
        #Reccursive function that checks if there is a next page 
        async def next_page(next_page_response: dict):
            if "nextPageToken" in next_page_response.keys():
                async with httpx.AsyncClient() as client:
                    payload["pageToken"]=next_page_response["nextPageToken"]
                    # payload["pageSize"]=20
                    response = await client.post(TEXT_SEARCH_URL, json=payload, headers=headers)
                    for place in response.json()["places"]:
                        result.append(place)
                    await next_page(response.json())
            else:
                return False
        await next_page(response.json())
                    
        #Calling "responce_fromatter" helper function to provide relevant fields for the output file
        data = await response_formatter(result,API_KEY,prompt_info,tiers)
        return {"places": data}
    else:
        raise HTTPException(status_code=401, detail="Invalid user credentials")
    