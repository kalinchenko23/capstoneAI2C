import streamlit as st
import folium

def initialize_state():

    # search area state variables
    #================================================================================================================
    # initialize and persist state variable that tracks the 'establishment search' input field
    if 'establishment_search_input' not in st.session_state:
        st.session_state['establishment_search_input'] = ''
    else:
        st.session_state['establishment_search_input'] = st.session_state['establishment_search_input']

    # initialize and persist state variable that tracks the 'location' input field
    if 'location_input' not in st.session_state:
        st.session_state['location_input'] = ''
    else:
        st.session_state['location_input'] = st.session_state['location_input']
    
    # initialize and persist state variable that tracks the 'location' input field
    if 'location_type' not in st.session_state:
        st.session_state['location_type'] = 'Lat/Lon'
    else:
        st.session_state['location_type'] = st.session_state['location_type']

    # initialize and persist state variable that tracks the validated location from the input field
    if 'location_validation_results' not in st.session_state:
        st.session_state['location_validation_results'] = None
    else:
        st.session_state['location_validation_results'] = st.session_state['location_validation_results']

    # init state variable that tracks the 'sw coordinate' input field
    if 'sw_coord' not in st.session_state:
        st.session_state['sw_coord'] = ''
    else:
        st.session_state['sw_coord'] = st.session_state['sw_coord']

    # init state variable that tracks the 'ne coordinate' input field
    if 'ne_coord' not in st.session_state:
        st.session_state['ne_coord'] = ''
    else:
        st.session_state['ne_coord'] = st.session_state['ne_coord']

    # initialize and persist state variable that tracks the center of the map
    if 'map_center' not in st.session_state:
        st.session_state['map_center'] = (39,34)
    else:
        st.session_state['map_center'] = st.session_state['map_center']

    # initialize and persist state variable that tracks the zoom level for the map
    if 'map_zoom_level' not in st.session_state:
        st.session_state['map_zoom_level'] = 2
    else:
        st.session_state['map_zoom_level'] = st.session_state['map_zoom_level']

    # initialize and persist feature group for points dropped on map
    if 'points_feature_group' not in st.session_state:
        st.session_state['points_feature_group'] = folium.FeatureGroup('points')
    else:
        st.session_state['points_feature_group'] = st.session_state['points_feature_group']

    #initialize and persist feature grooup for rectangles drawn/dropped on map
    if 'rectangle_feature_group' not in st.session_state:
        st.session_state['rectangle_feature_group'] = folium.FeatureGroup('rectangles')
    else:
        st.session_state['rectangle_feature_group'] = st.session_state['rectangle_feature_group']
    
    # initialize and persist state variable that tracks the map and the shapes drawn on it
    if 'map' not in st.session_state:
        st.session_state['map'] = {
            'all_drawings': [], 
            'last_active_drawing': [], 
            'zoom': st.session_state['map_zoom_level'], 
            'center': {'lat': 39, 'lng': 34}
        }
    else:
        st.session_state['map'] = st.session_state['map']

    # init state variable for tracking the box that is passed to google maps api
    if 'user_bounding_box' not in st.session_state:
        st.session_state['user_bounding_box'] = {}
    else:
        st.session_state['user_bounding_box'] = st.session_state['user_bounding_box']

    # init and persist state variable that is used (in a hacky way), to force the map to rerender
    if 'dummy_string_for_map_rerendering' not in st.session_state:
        st.session_state['dummy_string_for_map_rerendering'] = ''
    else: 
        st.session_state['dummy_string_for_map_rerendering'] = st.session_state['dummy_string_for_map_rerendering'] 

    # query options state variables
    #================================================================================================================
    # initialize and persist state variable that tracks the 'All' checkbox in 'Query Options'
    if 'all_fields_checkbox' not in st.session_state:
        st.session_state['all_fields_checkbox'] = False
    else:
        st.session_state['all_fields_checkbox'] = st.session_state['all_fields_checkbox']

    # initialize and persist state variable that tracks the 'Basic Data' checkbox in 'Query Options'
    if 'basic_data_checkbox' not in st.session_state:
        st.session_state['basic_data_checkbox'] = True
    else:
        st.session_state['basic_data_checkbox'] = st.session_state['basic_data_checkbox']

    # initialize and persist state variable that stores gmaps api key
    if 'google_maps_api_key' not in st.session_state:
        st.session_state['google_maps_api_key'] = ''
    else:
        st.session_state['google_maps_api_key'] = st.session_state['google_maps_api_key']

    # initialize and persist state variable that tracks the 'Include AI Review Summarization' checkbox in 'Query Options'
    if 'include_reviews_checkbox' not in st.session_state:
        st.session_state['include_reviews_checkbox'] = False
    else:
        st.session_state['include_reviews_checkbox'] = st.session_state['include_reviews_checkbox']

    # initialize and persist state variable that stores llm key
    if 'llm_key' not in st.session_state:
        st.session_state['llm_key'] = ''
    else:
        st.session_state['llm_key'] = st.session_state['llm_key']

    # initialize and persist state variable that tracks the 'Include AI Photo Captioning' checkbox in 'Query Options'
    if 'include_photo_captioning_checkbox' not in st.session_state:
        st.session_state['include_photo_captioning_checkbox'] = False
    else:
        st.session_state['include_photo_captioning_checkbox'] = st.session_state['include_photo_captioning_checkbox']

    # initialize and persist state variable that tracks which tiers of data the user wants
    if 'requested_tiers' not in st.session_state:
        st.session_state['requested_tiers'] = []
    else:
        st.session_state['requested_tiers'] = st.session_state['requested_tiers']
    
    # initialize and persist state variable that stores vlm key
    if 'vlm_key' not in st.session_state:
        st.session_state['vlm_key'] = ''
    else:
        st.session_state['vlm_key'] = st.session_state['vlm_key']

     # initialize and persist state variable that tracks the 'user_id' input field
    if 'vlm_input' not in st.session_state:
        st.session_state['vlm_input'] = ''
    else:
        st.session_state['vlm_input'] = st.session_state['vlm_input']
        
    # initialize and persist state variable that tracks the 'Include KML/KMZ Download' toggle in 'Query Options'
    if 'kmz_download_option' not in st.session_state:
        st.session_state['kmz_download_option'] = True
    else:
        st.session_state['kmz_download_option'] = st.session_state['kmz_download_option']

    # initialize and persist state variable that tracks the 'Include JSON Download' toggle in 'Query Options'
    if 'json_download_option' not in st.session_state:
        st.session_state['json_download_option'] = True
    else:
        st.session_state['json_download_option'] = st.session_state['json_download_option']

    # initialize and persist state variable that tracks wether a prediction has been generated for the current search area/term
    if 'price_predicted' not in st.session_state:
        st.session_state['price_predicted'] = False
    else:
        st.session_state['price_predicted'] = st.session_state['price_predicted']

    # initialize and persist state variable that stores the return from the POST request to the cost_estimator endpoint
    if 'price_prediction' not in st.session_state:
        st.session_state['price_prediction'] = {}
    else:
        st.session_state['price_prediction'] = st.session_state['price_prediction']

    # initialize and persist state variable that stores the current predictions predicted cost (based on selected tiers)
    if 'predicted_cost' not in st.session_state:
        st.session_state['predicted_cost'] = '-'
    else:
        st.session_state['predicted_cost'] = st.session_state['predicted_cost']

    # initialize and persist state variable that stores the current predictions predicted time (based on selected tiers)
    if 'predicted_time' not in st.session_state:
        st.session_state['predicted_time'] = '-'
    else: 
        st.session_state['predicted_time'] = st.session_state['predicted_time']

    # review + submit state variables
    #================================================================================================================
    # initialize and persist state variable that tracks wether a query has been submitted with the current params
    if 'query_submitted' not in st.session_state:
        st.session_state['query_submitted'] = False
    else:
        st.session_state['query_submitted'] = st.session_state['query_submitted']

    # initialize and persist state variable that tracks wether the duplicate query warning has been displayed
    if 'duplicate_query_warning_displayed' not in st.session_state:
        st.session_state['duplicate_query_warning_displayed'] = False
    else:
        st.session_state['duplicate_query_warning_displayed'] = st.session_state['duplicate_query_warning_displayed']