import base64
import requests
import streamlit as st
from datetime import datetime

# from .create_excel import json_to_excel
from .outputv5 import json_to_excel

# the 'generate_download_html' and 'auto_download_excel' are necessary becuase streamlit doesn't support the way we are trying to 
# handle the download. The BLUF is they want another button explicitly for downloading, whereas we want to 'auto download' upon submission

@st.fragment
def generate_download_html(base64_data, download_filename):
    """Creates an HTML + JavaScript snippet to auto-download a file."""
    html = f"""
    <html>
    <head>
    <title>Auto Download File</title>
    <script>
    function downloadExcel() {{
        var element = document.createElement('a');
        element.setAttribute('href', 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64_data}');
        element.setAttribute('download', '{download_filename}');
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }}
    window.onload = downloadExcel;
    </script>
    </head>
    <body>
    <p>Your download should start automatically. If not, <a href="#" onclick="downloadExcel()">click here</a>.</p>
    </body>
    </html>
    """
    return html

@st.fragment
def auto_download_excel(in_memory_file):
    # Injects JavaScript download logic into Streamlit using an in-memory file.
    formatted_time = datetime.now().strftime("%Y%m%d_%H%M")
    download_filename = f"{formatted_time}.xlsx"

    # Convert the in-memory Excel file to Base64
    in_memory_file.seek(0)  # Ensure we're at the start of the file
    file_data = in_memory_file.read()
    base64_data = base64.b64encode(file_data).decode("utf-8")

    # Generate the HTML for auto-download
    html = generate_download_html(base64_data, download_filename)
    st.components.v1.html(html, height=0)  # Embed auto-download script

@st.fragment
def text_search_post_request():
    """Handles the POST request, converts JSON response to Excel, and auto-downloads, with error handling."""
    request_body = {
        "text_query": st.session_state['establishment_search_input'],
        "lat_sw": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][0][1],
        "lng_sw": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][0][0],
        "lat_ne": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][2][1],
        "lng_ne": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][2][0],
        "user_id": st.session_state['user_id'],
        "token": st.session_state['token_input']
    }

    url = 'http://127.0.0.1:8080/search_nearby'

    try:
        # Make the POST request and get the response
        response = requests.post(url, json=request_body, timeout=10)  # Added timeout for graceful fail
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx, 5xx)
        
        # Check if the response contains valid JSON
        data = response.json()
        if not data:
            raise ValueError("Received empty response or invalid JSON.")
        
        # Generate Excel file in memory
        in_memory_file = json_to_excel(data)

        # Auto-download in browser
        auto_download_excel(in_memory_file)

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
def mock_post_request():
    import os
    import json
    """Mock version of the POST request that reads from a local JSON file instead of making an API call."""
    
    # Get the path to the current directory where the script is running
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the full file path to your JSON file
    file_path = os.path.join(current_dir, 'sample_response_modified.json')

    try:
        # Read the local JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if the data is valid (non-empty)
        if not data:
            raise ValueError("Received empty or invalid JSON from the local file.")
        
        # Generate Excel file in memory using the data read from the file
        in_memory_file = json_to_excel(data)

        # Auto-download in browser
        auto_download_excel(in_memory_file)

    except FileNotFoundError:
        # Handle case where the file does not exist
        st.error(f"File {file_path} not found. Please check the file path.")
    except json.JSONDecodeError:
        # Handle case where the JSON is invalid
        st.error(f"Error decoding JSON from the file {file_path}. Please check the file format.")
    except ValueError as e:
        # Handle case where the response is empty or invalid
        st.error(f"Invalid response received from the local file: {e}")
    except Exception as e:
        # Catch any other unforeseen errors
        st.error(f"An unexpected error occurred: {e}")



# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    generate_download_html()
    auto_download_excel()
    text_search_post_request()
    mock_post_request()