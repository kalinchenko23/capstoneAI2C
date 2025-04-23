import streamlit as st
import json
from styles.icons.icons import validation_error_icon

@st.fragment
def handle_post_request_errors(status_code, data):

    unexpected_error_prompt = "An Unexpected Error Occured. Please Try Again.\n If issue persists don't make additional queries and contact the team."

    # 400 - this is the code returned from the google maps api when you send an incorrect key
    if status_code == 400:
        data = data.json()
        try:
            detail = json.loads(data['detail'][data['detail'].index('{'):]) # this is required becuase the google maps API returns a goofy byte string instead of standard json when this happens

            if detail['error']['message'] == 'API key not valid. Please pass a valid API key.':
                st.error("Invalid Google Maps API Key provided. Please check your key and try again.", icon=validation_error_icon)
        
        # this will catch any 400 that isn't specifically from the google api. Havent run into it yet but its possible
        except:
            st.error(unexpected_error_prompt, icon=validation_error_icon)

    # 401 - this is the code returned from the openAI api when you send an incorrect key
    elif status_code == 401:
        detail = data.json()['detail']

        if detail == 'Your LLM key or endpoint is incorrect':
            st.error('Invalid OpenAI API LLM Key provided. Please check your key and try again.', icon=validation_error_icon)
        elif detail == 'Your VLM key or endpoint is incorrect':
            st.error('Invalid OpenAI API VLM Key provided. Please check your key and try again.', icon=validation_error_icon)
        else:
            st.error(unexpected_error_prompt, icon=validation_error_icon)

    # all other status codes
    else:
        st.error(unexpected_error_prompt, icon=validation_error_icon)