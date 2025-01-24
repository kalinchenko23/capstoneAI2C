from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.responses import FileResponse
from user_credentials_service import authenticate
from api_service_helper_functions import getting_street_view_image, download_photo
from typing import Optional
import httpx
import requests
import googlemaps
import json
import os


# Load the JSON secrets config
with open("secrets.json") as config_file:
    config = json.load(config_file)

app = FastAPI()
API_KEY = config["GOOGLE_API_KEY"]
GEOCODE_URL="https://maps.googleapis.com/maps/api/geocode/json"
BASE_URL_NEARBY_SEARCH = "https://places.googleapis.com/v1/places:searchNearby"
STREETVIEW_URL="https://maps.googleapis.com/maps/api/streetview"


#This FastAPI endpoint is used to perform geocoding (address to latitude/longitude conversion).
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
    for i in response.json()["places"]:
        location=i["formattedAddress"]
        filename=i["displayName"]["text"]
        await getting_street_view_image(location,filename,API_KEY,STREETVIEW_URL)
    
    #Calling "street view" helper function
    for i in response.json()["places"]:
        try:
            counter=1
            for photo in i["photos"]:
                name=photo["name"]
                uri=f"https://places.googleapis.com/v1/{name}/media?key={API_KEY}&maxHeightPx=400&maxWidthPx=400"
                file=i["displayName"]["text"]
                await download_photo(uri,filename=f"{file}{counter}")
                counter+=1
        except KeyError as e:
            pass

    return response.json()