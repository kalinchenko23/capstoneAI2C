from fastapi import FastAPI, Query, Body, HTTPException
import httpx
import json


async def getting_street_view_image(
    location: str,
    filename: str,
    key: str):
    """
    Fetches a Street View image from the Google Street View API and saves it as a file.

    Args:
        location (str): The location for the Street View image. Can be an address or latitude/longitude.
        filename (str): The name of the file to save the image as (without extension).
        key (str): The API key for authenticating with the Google Street View API.
        streetview_url (str): The base URL for the Google Street View API.

    Raises:
        HTTPException: If the `location` is not provided or the API request fails.

    Returns:
        bool: True if the image is successfully fetched and saved.
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

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch the image: {response.text}"
        )
    
    # Save the image to a temporary file
    with open(f"streetview_images/{filename}.jpg", "wb") as f:
        print(f"Saving image {filename}")
        f.write(response.content)
    
    return str(response.url)



async def download_photo(photo_uri: str, filename: str):
    """
    Downloads an image from the provided photo URI and saves it as a file.

    Args:
        photo_uri (str): The URL of the photo to download.
        filename (str): The name of the file to save the image as (without extension).

    Returns:
         bool: True if the image is successfully fetched and saved.
    """
    # Validate input
    if not photo_uri:
        raise ValueError("The 'photo_uri' parameter cannot be empty.")
    
    # Download the image
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(photo_uri)
        
        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to download the image. Status code: {response.status_code}")
        
        # Save the image to a file
        with open(f"photos/{filename}.jpg", "wb") as file:
            file.write(response.content)
    
    print(f"Image saved to {filename}")
    return True



async def response_formatter(responce,api_key):
    """
    Extracts specific fields from a JSON response provided by GoogleAPI and formats them into a structured list of dictionaries.

    Args:
        response (dict): The Google API JSON response containing place details.

    Returns:
        list: A list of formatted dictionaries containing relevant place information.
    """
    result=[]
    try:
        for place in responce["places"]:
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
                new_data["reviews"] = []
                for photo in place["reviews"]:
                    new_data["reviews"].append(photo["googleMapsUri"])
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
            new_data["street_view"]= "URL_CONTAINS_KEY_CAN'T_BE_EXPOSED" #await getting_street_view_image(location,filename,api_key)

            try:
                new_data["working_hours"]=place["regularOpeningHours"]["weekdayDescriptions"]
            except KeyError as ex:
                new_data["working_hours"]="Working hours are not provided"
            
            result.append(new_data)
    except KeyError as ex:
        return result
    return result