import streamlit as st

def initialize_state():
    # initialize state variable that tracks which navbar tab is active
    if 'active_tab' not in st.session_state:
      st.session_state['active_tab'] = 'User Credentials'

    # initialize state variable that tracks the 'user_id' input field
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = ''

    # initialize state variable that tracks the 'token' input field
    if 'token_input' not in st.session_state:
        st.session_state['token_input'] = ''

    # initialize state variable that tracks the 'location' input field
    if 'location_input' not in st.session_state:
        st.session_state['location_input'] = ''
    
    # initialize state variable that tracks the 'location' input field
    if 'location_type' not in st.session_state:
        st.session_state['location_type'] = 'Lat/Lon'
    
    # initialize state variable that tracks the 'establishment search' input field
    if 'establishment_search_input' not in st.session_state:
        st.session_state['establishment_search_input'] = ''

    # initialize state variable that tracks the map and the shapes drawn on it
    if 'map' not in st.session_state:
        st.session_state['map'] = {
            'all_drawings': [], 
            'last_active_drawing': []
        }

    # initialize state variable that tracks the 'user_id' input field
    if 'image_analysis_input' not in st.session_state:
        st.session_state['image_analysis_input'] = ''

    # initialize state variable that tracks the 'All' checkbox in 'Query Options'
    if 'all_fields_checkbox' not in st.session_state:
        st.session_state['all_fields_checkbox'] = False

    # initialize state variable that tracks the 'Basic Data' checkbox in 'Query Options'
    if 'basic_data_checkbox' not in st.session_state:
        st.session_state['basic_data_checkbox'] = True

    # initialize state variable that tracks the 'Include AI Review Summarization' checkbox in 'Query Options'
    if 'include_reviews_checkbox' not in st.session_state:
        st.session_state['include_reviews_checkbox'] = False

    # initialize state variable that tracks the 'Include AI Photo Captioning' checkbox in 'Query Options'
    if 'include_photo_captioning_checkbox' not in st.session_state:
        st.session_state['include_photo_captioning_checkbox'] = False

    # initialize state variable that tracks the 'Include KML/KMZ Download' toggle in 'Query Options'
    if 'kml_download_option' not in st.session_state:
        st.session_state['kml_download_option'] = True


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    initialize_state()