import streamlit as st
import requests
import os
import json

@st.fragment
def cost_estimator():
    st.write('call the endpoint...')

    request_body = {
                    "text_query":"продуктовий магазин",
                    "lat_sw":50.468330,
                    "lng_sw":30.509044,
                    "lat_ne":50.472441,
                    "lng_ne": 30.519623, 
                    "google_api_key":"AIzaSyDu8FoGGPCgYmyF12dNGj475bTTPZMYtkk"
                    }
    
    # kubernetes deployment url
    url = 'http://127.0.0.1:8000/estimator'

    # local deployment url
    # url = 'http://backend:8000/estimator'

    response = requests.post(url, json=request_body)
    response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx, 5xx)

    # Check if the response contains valid JSON
    data = response.json()
    if not data:
        st.error(f'there is no data')
    else:
        st.write(data)



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