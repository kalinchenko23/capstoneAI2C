from fastapi import FastAPI, Body, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from api_service_helper_functions import response_formatter
from typing import Optional
from estimator import cost_time_predict 
from fastapi.responses import JSONResponse
from kmz_converter import json_to_kmz
from excel_converter import json_to_excel
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Any, Optional
import httpx

#Defining global variables
app = FastAPI()
TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
GEOCODE_URL="https://maps.googleapis.com/maps/api/geocode/json"

#Adding CORS policies
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all origins (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Excel download endpoint
@app.post("/get_excel")
async def get_excel(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    excel_io = json_to_excel(data)
    return StreamingResponse(
        excel_io,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=locations.xlsx"},
    )
# KMZ Request Model
class KMZRequest(BaseModel):
    data: Any  # the JSON from /search_nearby
    bbox: List[List[float]]  # e.g., [[lng, lat], [lng, lat], ...]
    search_term: str

#KMZ download endpoint
@app.post("/get_kmz")
async def get_kmz(request: KMZRequest):
    wrapped_data = {"places": request.data}
    try:
        kmz_file = json_to_kmz(wrapped_data, request.bbox, request.search_term)
        print("KMZ file created successfully")
        return StreamingResponse(
            kmz_file,
            media_type="application/vnd.google-earth.kmz",
            headers={
                "Content-Disposition": f"attachment; filename={request.search_term.replace(' ', '_')}.kmz"
            }
        )
    except Exception as e:
        print("Error in KMZ generation:", e)
        raise HTTPException(status_code=500, detail=f"KMZ conversion error: {str(e)}")

@app.post("/search_nearby")
async def search_nearby_places(text_query: str =Body(),
                               lat_sw: float = Body(),
                               lng_sw: float = Body(),
                               lat_ne: float = Body(),
                               lng_ne: float = Body(),
                               prompt_info: str =Body(),
                               tiers: Optional[list] = Body(default=None),
                               google_api_key: str = Body(),
                               llm_key: Optional[str] = Body(default=None),
                               vlm_key: Optional[str] = Body(default=None),
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
    print()
    async with httpx.AsyncClient() as client:
        response = await client.post(TEXT_SEARCH_URL, json=payload, headers=headers)
        
        
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error from Google API: {response.text}"
        )
    
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

    result = response.json().get("places", {})
                
    #Calling "responce_fromatter" helper function to provide relevant fields for the output file
    data = await response_formatter(result,google_api_key,prompt_info,tiers,llm_key,vlm_key)
    return JSONResponse(content=data)

@app.post("/estimator")
async def search_nearby_places(text_query: str =Body(),
                               lat_sw: float = Body(),
                               lng_sw: float = Body(),
                               lat_ne: float = Body(),
                               lng_ne: float = Body(),
                               google_api_key: str = Body(),
                               pageToken: Optional[str] = Body(default=None),
                               fieldMask: str = Body(default="places.id,nextPageToken")):
    
    """
    This endpoint performs a search for places in order to estimate how long 
    a main query will take and how much will it cost.
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
    return  cost_time_predict(len(result))
