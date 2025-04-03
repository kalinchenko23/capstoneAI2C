from fastapi import FastAPI, Query, Body, HTTPException, Response
from api_service_helper_functions import getting_street_view_image, response_formatter
from typing import Optional
import httpx
import json
import re


#Defining global variables
app = FastAPI()

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
GEOCODE_URL="https://maps.googleapis.com/maps/api/geocode/json"

@app.post("/search_nearby")
async def search_nearby_places(text_query: str =Body(),
                               lat_sw: float = Body(),
                               lng_sw: float = Body(),
                               lat_ne: float = Body(),
                               lng_ne: float = Body(),
                               prompt_info: str =Body(),
                               tiers: list = Body(),
                               google_api_key: str = Body(),
                               llm_key: str = Body(),
                               vlm_key: str = Body(),
                               pageToken: Optional[str] = Body(default=None),
                               fieldMask: str = Body(default="places.displayName,places.types,places.websiteUri,places.nationalPhoneNumber,places.formattedAddress,places.location,places.reviews,places.photos,places.regularOpeningHours,places.googleMapsUri,nextPageToken")):
    
    """
    This endpoint performs a text-based search for places within a specified bounding box.
    It returns places that match the given text query and includes pagination support.
    """
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": google_api_key,
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
    data = await response_formatter(result,google_api_key,prompt_info,tiers,llm_key,vlm_key)
    return {"places": data}

    