from fastapi import FastAPI, Query, Body, HTTPException
import httpx



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

async def getting_street_view_image(
    location: str,
    filename: str,
    key: str,
    streetview_url: str):

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
    url = f"{streetview_url}?{query}"

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
    
    return True



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