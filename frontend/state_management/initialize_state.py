import streamlit as st
import folium

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

    # initialize state variable that tracks the validated location from the input field
    if 'location_validation_results' not in st.session_state:
        st.session_state['location_validation_results'] = None

    # init state variable that tracks the 'sw coordinate' input field
    if 'sw_coord' not in st.session_state:
        st.session_state['sw_coord'] = ''

    # init state variable that tracks the 'ne coordinate' input field
    if 'ne_coord' not in st.session_state:
        st.session_state['ne_coord'] = ''

    # initialize state variable that tracks the center of the map
    if 'map_center' not in st.session_state:
        st.session_state['map_center'] = (0,0)

    # initialize state variable that tracks the zoom level for the map
    if 'map_zoom_level' not in st.session_state:
        st.session_state['map_zoom_level'] = 2

    # initialize feature group for points dropped on map
    if 'points_feature_group' not in st.session_state:
        st.session_state['points_feature_group'] = folium.FeatureGroup('points')

    #initialize feature grooup for rectangles drawn/dropped on map
    if 'rectangle_feature_group' not in st.session_state:
        st.session_state['rectangle_feature_group'] = folium.FeatureGroup('rectangles')
    
    # initialize state variable that tracks the 'establishment search' input field
    if 'establishment_search_input' not in st.session_state:
        st.session_state['establishment_search_input'] = ''

    # initialize state variable that tracks the map and the shapes drawn on it
    if 'map' not in st.session_state:
        st.session_state['map'] = {
            'all_drawings': [], 
            'last_active_drawing': [], 
            'zoom': 2, 
            'center': {'lat': 0, 'lng': 0}
        }

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

     # initialize state variable that tracks the 'user_id' input field
    if 'vlm_input' not in st.session_state:
        st.session_state['vlm_input'] = ''
        
    # initialize state variable that tracks the 'Include KML/KMZ Download' toggle in 'Query Options'
    if 'kml_download_option' not in st.session_state:
        st.session_state['kml_download_option'] = True


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    initialize_state()