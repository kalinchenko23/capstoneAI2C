import pytest
import sys
import os 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api_service_helper_functions import response_formatter


# Sample response data for testing
sample_response = {
    "places": [
        {
            "displayName": {"text": "Place 1"},
            "websiteUri": "http://place1.com",
            "nationalPhoneNumber": "+1234567890",
            "formattedAddress": "123 Place St",
            "location": {"latitude": 34.0522, "longitude": -118.2437},
            "reviews": ["Great place!", "Would visit again!"],
            "photos": ["photo1.jpg", "photo2.jpg"],
            "regularOpeningHours": {"weekdayDescriptions": ["9 AM - 5 PM", "Closed on Sundays"]}
        }
    ]
}

empty_place_response = {
    "places": [
        {}
    ]
}

no_places_response = {}

# Test 1: Testing normal response with expected values
def test_response_formatter_normal():
    result = response_formatter(sample_response)
    assert isinstance(result, list)  # The output should be a list
    assert len(result) == 1  # Only one place in the list
    assert result[0]["name"] == "Place 1"
    assert result[0]["website"] == "http://place1.com"
    assert result[0]["phone_number"] == "+1234567890"
    assert result[0]["address"] == "123 Place St"
    assert result[0]["latitude"] == 34.0522
    assert result[0]["longitude"] == -118.2437
    assert result[0]["reviews"] == ["Great place!", "Would visit again!"]
    assert result[0]["photos"] == ["photo1.jpg", "photo2.jpg"]
    assert result[0]["working_hours"] == ["9 AM - 5 PM", "Closed on Sundays"]

# Test 2: Testing a response with missing place data
def test_response_formatter_empty_place():
    result = response_formatter(empty_place_response)
    assert isinstance(result, list)  # The output should still be a list
    assert len(result) == 1  # Still one place in the list
    assert result[0]["name"] == "Name is not provided"
    assert result[0]["website"] == "Website is not provided"
    assert result[0]["phone_number"] == "Phone number is not provided"
    assert result[0]["address"] == "Address number is not provided"
    assert result[0]["latitude"] == "Latitude is not provided"
    assert result[0]["longitude"] == "Longitude is not provided"
    assert result[0]["reviews"] == "Reviews are not provided"
    assert result[0]["photos"] == "Photos are not provided"
    assert result[0]["working_hours"] == "Working hours are not provided"

# Test 3: Testing a response with no places key
def test_response_formatter_no_places():
    result = response_formatter(no_places_response)
    assert result == []  # The result should be an empty list, as there are no places

# Test 4: Testing a response with a missing location field
def test_response_formatter_missing_location():
    response = {
        "places": [
            {
                "displayName": {"text": "Place without location"}
            }
        ]
    }
    result = response_formatter(response)
    assert result[0]["latitude"] == "Latitude is not provided"
    assert result[0]["longitude"] == "Longitude is not provided"