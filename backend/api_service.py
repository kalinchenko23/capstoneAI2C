from fastapi import FastAPI, Body, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Any

from api_service_helper_functions import response_formatter
from estimator import cost_time_predict
from kmz_converter import json_to_kmz
from excel_converter import json_to_excel
import httpx

# ---------------------- FastAPI Setup ----------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- Constants ----------------------

TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# ---------------------- Request Models ----------------------

class KMZRequest(BaseModel):
    data: Any
    bbox: List[List[float]]
    search_term: str

class EstimatorRequest(BaseModel):
    text_query: str
    lat_sw: float
    lng_sw: float
    lat_ne: float
    lng_ne: float
    google_api_key: str
    pageToken: Optional[str] = None
    fieldMask: Optional[str] = "places.id,nextPageToken"

class SearchNearbyRequest(BaseModel):
    text_query: str
    lat_sw: float
    lng_sw: float
    lat_ne: float
    lng_ne: float
    prompt_info: str
    tiers: Optional[list] = None
    google_api_key: str
    llm_key: Optional[str] = None
    vlm_key: Optional[str] = None
    pageToken: Optional[str] = None
    fieldMask: Optional[str] = (
        "places.displayName,places.types,places.websiteUri,places.nationalPhoneNumber,"
        "places.formattedAddress,places.location,places.reviews,places.photos,"
        "places.regularOpeningHours,places.googleMapsUri,nextPageToken"
    )

# ---------------------- Helper Functions ----------------------

def build_payload(text_query, lat_sw, lng_sw, lat_ne, lng_ne, page_token=None):
    return {
        "textQuery": text_query,
        "locationRestriction": {
            "rectangle": {
                "low": {"latitude": lat_sw, "longitude": lng_sw},
                "high": {"latitude": lat_ne, "longitude": lng_ne}
            }
        },
        "pageToken": page_token
    }

async def fetch_all_places(payload, headers) -> List[dict]:
    """Fetches all paginated places from Google Places API."""
    result = []

    async def fetch_page(p_token=None):
        if p_token:
            payload["pageToken"] = p_token

        async with httpx.AsyncClient() as client:
            response = await client.post(TEXT_SEARCH_URL, json=payload, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            data = response.json()
            result.extend(data.get("places", []))
            if "nextPageToken" in data:
                await fetch_page(data["nextPageToken"])

    await fetch_page(payload.get("pageToken"))
    return result

# ---------------------- Endpoints ----------------------

@app.post("/get_excel")
async def get_excel(request: Request):
    try:
        data = await request.json()
        excel_io = json_to_excel(data)
        return StreamingResponse(
            excel_io,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=locations.xlsx"},
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON input for Excel conversion.")


@app.post("/get_kmz")
async def get_kmz(request: KMZRequest):
    try:
        wrapped_data = {"places": request.data}
        kmz_file = json_to_kmz(wrapped_data, request.bbox, request.search_term)
        return StreamingResponse(
            kmz_file,
            media_type="application/vnd.google-earth.kmz",
            headers={
                "Content-Disposition": f"attachment; filename={request.search_term.replace(' ', '_')}.kmz"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KMZ conversion error: {str(e)}")


@app.post("/search_nearby")
async def search_nearby_places(req: SearchNearbyRequest):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": req.google_api_key,
        "X-Goog-FieldMask": req.fieldMask
    }

    payload = build_payload(req.text_query, req.lat_sw, req.lng_sw, req.lat_ne, req.lng_ne, req.pageToken)
    places = await fetch_all_places(payload, headers)
    formatted_data = await response_formatter(places, req.google_api_key, req.prompt_info, req.tiers, req.llm_key, req.vlm_key)
    return JSONResponse(content=formatted_data)


@app.post("/estimator")
async def estimate_query(req: EstimatorRequest):
    """
    Estimates the total cost and time for a full query.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": req.google_api_key,
        "X-Goog-FieldMask": req.fieldMask
    }

    payload = build_payload(req.text_query, req.lat_sw, req.lng_sw, req.lat_ne, req.lng_ne, req.pageToken)
    places = await fetch_all_places(payload, headers)
    return cost_time_predict(len(places))
