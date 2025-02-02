from fastapi import FastAPI, Query, Body, HTTPException, Response
from user_credentials_service import authenticate
from api_service_helper_functions import getting_street_view_image, download_photo, response_formatter
from typing import Optional
import httpx
import json



# Load the JSON secrets config
with open("secrets.json") as config_file:
    config = json.load(config_file)

#Defining global variables
app = FastAPI()
API_KEY = config["GOOGLE_API_KEY"]
BASE_URL_NEARBY_SEARCH = "https://places.googleapis.com/v1/places:searchNearby"
STREETVIEW_URL="https://maps.googleapis.com/maps/api/streetview"


@app.post("/search_nearby")
async def search_nearby_places(lat: float = Body(),
                               lng: float = Body(),
                               rad: float = Body(),
                               includedTypes: Optional[list] =Body(default=None),
                               user_id = Body(), token: str =Body(),
                               maxResultCount: int = Body(default=None),
                               fieldMask: str = Body(default="places.displayName,places.websiteUri,places.nationalPhoneNumber,places.formattedAddress,places.location,places.reviews,places.photos,places.regularOpeningHours,places.googleMapsUri,places.googleMapsLinks")):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": fieldMask
    }

    payload={
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng
                    },
                    "radius": rad
            }},
    "includedTypes": includedTypes,
    "maxResultCount": maxResultCount
    
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL_NEARBY_SEARCH, json=payload, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error from Google API: {response.text}"
        )
    
    #Calling "street view" helper function 
    # for i in response.json()["places"]:
    #     location=i["formattedAddress"]
    #     filename=i["displayName"]["text"]
    #     await getting_street_view_image(location,filename,API_KEY,STREETVIEW_URL)
    
    # #Calling "download_photo" helper function
    # for i in response.json()["places"]:
    #     try:
    #         counter=1
    #         for photo in i["photos"]:
    #             name=photo["name"]
    #             uri=f"https://places.googleapis.com/v1/{name}/media?key={API_KEY}&maxHeightPx=400&maxWidthPx=400"
    #             file=i["displayName"]["text"]
    #             await download_photo(uri,filename=f"{file}{counter}")
    #             counter+=1
    #     except KeyError as e:
    #         pass
    
    #Calling "responce_fromatter" helper function to provide relevant fields for the output file
    data=response_formatter(response.json())
    return  {"places": data}