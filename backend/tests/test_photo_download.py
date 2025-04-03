import pytest
import httpx
from unittest import mock
import sys
import os 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_service_helper_functions import download_photo  

@pytest.mark.asyncio
async def test_download_photo_failure_invalid_uri():
    # Test for an empty photo_uri, should raise a ValueError
    with pytest.raises(ValueError, match="The 'photo_uri' parameter cannot be empty."):
        await download_photo("", "test_photo")

@pytest.mark.asyncio
async def test_download_photo_http_error():
    # Mock the response for an HTTP error (non-200 status code)
    mock_response = mock.AsyncMock(httpx.Response)
    mock_response.status_code = 404
    mock_response.content = b"Not Found"

    # Mock the client.get method to return our mock error response
    with mock.patch("httpx.AsyncClient.get", return_value=mock_response):
        with pytest.raises(Exception, match="Failed to download the image. Status code: 404"):
            await download_photo("http://example.com/photo.jpg", "test_photo")