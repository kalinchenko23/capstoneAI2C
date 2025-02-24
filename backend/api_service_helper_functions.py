from fastapi import FastAPI, Query, Body, HTTPException
from llm_service import get_review_summary
import httpx
import json
import base64
from datetime import datetime

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
    if location:
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



async def get_photo(photo_uri: str):
    """
    Get and encode an image from the provided photo URI.

    Returns:
         str: Base64 encoded string.
    """
    # Validate input
    if not photo_uri:
        raise ValueError("The 'photo_uri' parameter cannot be empty.")
    
    # Base64 encode image
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(photo_uri)
    encoded_string = base64.b64encode(response.content).decode('utf-8')
    return encoded_string


async def response_formatter(responce,api_key):
    """
    Extracts specific fields from a JSON response provided by GoogleAPI and formats them into a structured list of dictionaries.

    Args:
        response (dict): The Google API JSON response containing place details.

    Returns:
        list: A list of formatted dictionaries containing relevant place information.
    """
    result=[]

    for place in responce:
        new_data={}
        try:
            new_data["name"]=place["displayName"]["text"]
        except KeyError as ex:
            new_data["name"]="Name is not provided"
        try:
            new_data["website"]=place["websiteUri"]
        except KeyError as ex:
            new_data["website"]="Website is not provided"
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
            
        try:

            # new_data["reviews_summary"] = get_review_summary(place["reviews"])
            
            new_data["reviews"] = []
            ratings=[]
            times=[]
            for review in place["reviews"]:
                #appends review link and origianl language
                r={}
                r["review_url"]=review["googleMapsUri"]
                r["text"]=review["text"]["text"]
                r["original_text"]=review["originalText"]["text"]
                r["original_language"]=review["originalText"]["languageCode"]
                r["author_name"]=review["authorAttribution"]["displayName"]
                r["author_url"]=review["authorAttribution"]["uri"]
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

        try:
            new_data["photos"] = []
            for photo in place["photos"]:
                new_data["photos"].append(photo["googleMapsUri"])
        except KeyError as ex:
            new_data["photos"]="Photos are not provided"

        location=place["formattedAddress"]
        filename=place["displayName"]["text"]
        new_data["street_view"]= "URL_CONTAINS_KEY_CAN'T_BE_EXPOSED" #await getting_street_view_image(location,filename,api_key)[0]

        try:
            new_data["working_hours"]=place["regularOpeningHours"]["weekdayDescriptions"]
        except KeyError as ex:
            new_data["working_hours"]="Working hours are not provided"
        
        result.append(new_data)
        
    return result

