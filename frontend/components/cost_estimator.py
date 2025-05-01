import streamlit as st
import requests
import os
import json

from components.validation_functions import validate_establishment_search, validate_bounding_box, validate_google_maps_api_key
from .handle_post_request_errors import handle_post_request_errors
from styles.icons.icons import no_results_icon
from styles.icons.icons import validation_error_icon

def cost_estimator():
    validated_establishment_search = validate_establishment_search(st.session_state['establishment_search_input'])
    validated_bounding_box = validate_bounding_box(st.session_state['user_bounding_box'])
    validated_google_maps_api_key = validate_google_maps_api_key(st.session_state['google_maps_api_key'])

    request_body = {
                    "text_query": validated_establishment_search,
                    "lat_sw": validated_bounding_box['geometry']['coordinates'][0][0][1],
                    "lng_sw": validated_bounding_box['geometry']['coordinates'][0][0][0], 
                    "lat_ne": validated_bounding_box['geometry']['coordinates'][0][2][1], 
                    "lng_ne": validated_bounding_box['geometry']['coordinates'][0][2][0], 
                    "google_api_key": validated_google_maps_api_key,
                    }
    
    # local deployment url
    url = 'http://backend:8000/estimator'
    # url = 'http://127.0.0.1:8000/estimator'

    try:
        response = requests.post(url, json=request_body)

        # 200 - successful query from google maps api
        if response.status_code == 200:
            st.session_state['price_predicted'] = True
            
            data = response.json()
            if data:
                st.session_state['price_prediction'] = data
            else:
                st.session_state['price_prediction'] = {}

            st.rerun()

        else: # any status code that isn't a 200 from the google maps api
            handle_post_request_errors(response.status_code, response)
            return
    
    except requests.exceptions.ConnectionError:
        st.error('Could not establish a connection to the backend when making the post request.', icon=validation_error_icon)

    

@st.fragment
def mock_cost_estimator():
    """Mock version of the POST request that reads from a local JSON file instead of making an API call."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'estimator_results.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data:
            raise ValueError("Received empty or invalid JSON from the local file.")
        else:
            st.session_state['price_prediction'] = data

    except FileNotFoundError:
        st.error(f"File {file_path} not found. Please check the file path.")
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from the file {file_path}. Please check the file format.")
    except ValueError as e:
        st.error(f"Invalid response received from the local file: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    cost_estimator()
    mock_cost_estimator()
