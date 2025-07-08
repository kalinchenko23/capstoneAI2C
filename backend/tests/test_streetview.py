import pytest
import httpx
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
import sys
import os 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_service_helper_functions import getting_street_view_image  

@pytest.mark.asyncio
async def test_getting_street_view_image_missing_location():
    """Test if the function raises an HTTPException when location is missing."""
    with pytest.raises(HTTPException) as exc_info:
        await getting_street_view_image("", "test_image", "fake_api_key", "https://maps.googleapis.com/maps/api/streetview")

    assert exc_info.value.status_code == 400
    assert "You must provide a 'location'" in exc_info.value.detail


@pytest.mark.asyncio
async def test_getting_street_view_image_successful():
    """Test a successful image retrieval with a mocked HTTP response."""
    
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.content = b"fake_image_data"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await getting_street_view_image("New York, NY", "test_image", "fake_api_key", "https://maps.googleapis.com/maps/api/streetview")
    
    assert result is True


@pytest.mark.asyncio
async def test_getting_street_view_image_api_failure():
    """Test if the function raises an HTTPException when the API returns an error."""
    
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(HTTPException) as exc_info:
            await getting_street_view_image("Los Angeles, CA", "test_image", "fake_api_key", "https://maps.googleapis.com/maps/api/streetview")

    assert exc_info.value.status_code == 500
    assert "Failed to fetch the image" in exc_info.value.detail