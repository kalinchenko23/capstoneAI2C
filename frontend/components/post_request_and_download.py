import base64
import requests
import streamlit as st
from datetime import datetime
import os
import json

from .create_excel import json_to_excel
from .create_kmz import json_to_kmz

# the 'generate_download_html' and 'auto_download_excel' are necessary becuase streamlit doesn't support the way we are trying to 
# handle the download. The BLUF is they want another button explicitly for downloading, whereas we want to 'auto download' upon submission

@st.fragment
def generate_download_html(base64_data, download_filename, mime_type):
    """Creates an HTML + JavaScript snippet to auto-download a file."""
    html = f"""
    <html>
    <head>
    <title>Auto Download File</title>
    <script>
    function downloadFile() {{
        var element = document.createElement('a');
        element.setAttribute('href', 'data:{mime_type};base64,{base64_data}');
        element.setAttribute('download', '{download_filename}');
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }}
    window.onload = downloadFile;
    </script>
    </head>
    <body>
    <p>Your download should start automatically. If not, <a href="#" onclick="downloadFile()">click here</a>.</p>
    </body>
    </html>
    """
    return html

@st.fragment
def auto_download_file(in_memory_file, file_extension, mime_type):
    formatted_time = datetime.now().strftime("%Y%m%d_%H%M")
    download_filename = f"{formatted_time}.{file_extension}"
    in_memory_file.seek(0)
    file_data = in_memory_file.read()
    base64_data = base64.b64encode(file_data).decode("utf-8")
    html = generate_download_html(base64_data, download_filename, mime_type)
    st.components.v1.html(html, height=0)

@st.fragment
def text_search_post_request(validated_establishment_search,
                             validated_bounding_box,
                             validated_photo_caption_keywords,
                             requested_tiers,
                             validated_google_maps_api_key,
                             validated_llm_key, 
                             validated_vlm_key, 
                             bbox_tuples
                            ):
    """Handles the POST request, converts JSON response to Excel, and auto-downloads, with error handling."""

    request_body = {
        "text_query": validated_establishment_search, # establishment search
        "lat_sw": validated_bounding_box['geometry']['coordinates'][0][0][1],
        "lng_sw": validated_bounding_box['geometry']['coordinates'][0][0][0], 
        "lat_ne": validated_bounding_box['geometry']['coordinates'][0][2][1], 
        "lng_ne": validated_bounding_box['geometry']['coordinates'][0][2][0], 
        "prompt_info": validated_photo_caption_keywords,  # vlm input
        "tiers": requested_tiers, # data to include in report
        "google_api_key": validated_google_maps_api_key,
        "llm_key": validated_llm_key, 
        "vlm_key": validated_vlm_key
    }

    st.write(f'post request with following body:\n {request_body}')

    url = 'http://127.0.0.1:8080/search_nearby'

    try:
        # Make the POST request and get the response
        response = requests.post(url, json=request_body)
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx, 5xx)
        
        # Check if the response contains valid JSON
        data = response.json()
        if not data:
            raise ValueError("Received empty response or invalid JSON.")
        
        # Generate Excel file in memory
        excel_file = json_to_excel(data)
        auto_download_file(excel_file, "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # conditional to check if a kmz should be returned to the user
        if st.session_state['kmz_download_option']:
            # Generate KMZ file in memory
            kmz_file = json_to_kmz(data, bbox_tuples, validated_establishment_search)
            auto_download_file(kmz_file, "kmz", "application/vnd.google-earth.kmz")

    except requests.exceptions.Timeout:
        # Handle timeout error (e.g., server takes too long to respond)
        st.error("The request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        # Handle other request exceptions (e.g., network issues, bad status codes)
        st.error(f"An error occurred while making the request: {e}")
    except ValueError as e:
        # Handle case where the response is empty or invalid JSON
        st.error(f"Invalid response received from the API: {e}")
    except Exception as e:
        # Catch any other unforeseen errors
        st.error(f"An unexpected error occurred: {e}")

@st.fragment
def mock_post_request(bbox_tuples, search_term):
    """Mock version of the POST request that reads from a local JSON file instead of making an API call."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'sample_response_modified.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data:
            raise ValueError("Received empty or invalid JSON from the local file.")
        
        # Generate Excel file in memory
        excel_file = json_to_excel(data)
        auto_download_file(excel_file, "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # conditional to check if a kmz should be returned to the user
        if st.session_state['kmz_download_option']:
            # Generate KMZ file in memory
            kmz_file = json_to_kmz(data, bbox_tuples, search_term)
            auto_download_file(kmz_file, "kmz", "application/vnd.google-earth.kmz")
        



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
    generate_download_html()
    auto_download_file()
    text_search_post_request()
    mock_post_request()