import streamlit as st
import requests
import json
import base64
import streamlit.components.v1 as components
from datetime import datetime

# this is streamlit shenanigans to enable the "auto" download
def download_button(object_to_download, download_filename):
    # Convert the object to a JSON string (ensure it's pretty-printed with unicode characters intact)
    object_to_download_str = json.dumps(object_to_download, ensure_ascii=False, indent=4)

    # Encode the JSON string into base64
    try:
        b64 = base64.b64encode(object_to_download_str.encode('utf-8')).decode('utf-8')
    except AttributeError as e:
        b64 = base64.b64encode(object_to_download_str).decode('utf-8')

    # Generate the download link with embedded base64 data
    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:text/json;base64,{b64}" download="{download_filename}">')[0].click()
    </script>
    </head>
    </html>
    """
    
    return dl_link

def download_df(data):
    formatted_time = datetime.now().strftime("%Y%m%d_%H%M")
    components.html(
        download_button(data, f'{formatted_time}.json'),
        height=0,
)
    
def nearby_search_post_request():

    request_body = {
        'lat': float(st.session_state['validated_location'][0]), 
        'lng': float(st.session_state['validated_location'][1]), 
        'rad': float(st.session_state['validated_search_radius']),
        'user_id': str(st.session_state['validated_user_id']),
        'token': str(st.session_state['validated_token']),
        'includedTypes': [], 
        'maxResultCount': 20
    }

    url = 'http://127.0.0.1:8080/search_nearby'

    response = requests.post(url, json=request_body)
    data = json.loads(response.content)

    
    download_df(data)




