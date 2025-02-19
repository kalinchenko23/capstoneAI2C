import streamlit as st

def initialize_state():
    # initialize state variable that tracks which navbar tab is active
    if 'active_tab' not in st.session_state:
      st.session_state['active_tab'] = 'User Credentials'

    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = ''

    if 'token_input' not in st.session_state:
        st.session_state['token_input'] = ''

    if 'image_analysis_input' not in st.session_state:
        st.session_state['image_analysis_input'] = ''

    if 'location_input' not in st.session_state:
        st.session_state['location_input'] = ''

    if 'all_fields_checkbox' not in st.session_state:
        st.session_state['all_fields_checkbox'] = False

    if 'basic_data_checkbox' not in st.session_state:
        st.session_state['basic_data_checkbox'] = True

    if 'include_reviews_checkbox' not in st.session_state:
        st.session_state['include_reviews_checkbox'] = False

    if 'include_photo_captioning_checkbox' not in st.session_state:
        st.session_state['include_photo_captioning_checkbox'] = False

    if 'kml_download_option' not in st.session_state:
        st.session_state['kml_download_option'] = False

    if 'establishment_search_input' not in st.session_state:
        st.session_state['establishment_search_input'] = ''

    if 'map' not in st.session_state:
        st.session_state['map'] = {
            'all_drawings': [], 
            'last_active_drawing': []
        }


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    initialize_state()