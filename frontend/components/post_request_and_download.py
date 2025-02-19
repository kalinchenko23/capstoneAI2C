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
    
def text_search_post_request():
    request_body = {
            "text_query": st.session_state['establishment_search_input'], 
            "lat_sw": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][0][1], 
            "lng_sw": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][0][0], 
            "lat_ne": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][2][1], 
            "lng_ne": st.session_state['map']['last_active_drawing']['geometry']['coordinates'][0][2][0],
            "user_id": "user123", 
            "token": ""
            # "user_id": st.session_state['user_id'], 
            # "token": st.session_state['token_input']
            }

    url = 'http://127.0.0.1:8080/search_nearby'

    response = requests.post(url, json=request_body)
    data = json.loads(response.content)

    
    download_df(data)

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    download_button()
    download_df()
    text_search_post_request()


