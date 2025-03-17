import streamlit as st

# seems pretty clunky but...
# with the new implementation of the custom tabs function (which enables conditional rendering across the tabs), 
# the state session object was being erased and re created every tab change
# by adding this to the callback function, input values persist across tab changes
# this is absolutely necessary if we keep the faux tabs
def persist_state():
    st.session_state['user_id'] = st.session_state['user_id']
    st.session_state['token_input'] = st.session_state['token_input']
    st.session_state['location_input'] = st.session_state['location_input']
    st.session_state['location_type'] = st.session_state['location_type']
    st.session_state['location_validation_results'] = st.session_state['location_validation_results']
    st.session_state['sw_coord'] = st.session_state['sw_coord']
    st.session_state['ne_coord'] = st.session_state['ne_coord']
    st.session_state['map_center'] = st.session_state['map_center']
    st.session_state['map_zoom_level'] = st.session_state['map_zoom_level']
    st.session_state['points_feature_group'] = st.session_state['points_feature_group']
    st.session_state['rectangle_feature_group'] = st.session_state['rectangle_feature_group']
    st.session_state['establishment_search_input'] = st.session_state['establishment_search_input']
    st.session_state['map'] = st.session_state['map']
    st.session_state['user_bounding_box'] = st.session_state['user_bounding_box']
    st.session_state['vlm_input'] = st.session_state['vlm_input']
    st.session_state['all_fields_checkbox'] = st.session_state['all_fields_checkbox']
    st.session_state['basic_data_checkbox'] = st.session_state['basic_data_checkbox']
    st.session_state['include_reviews_checkbox'] = st.session_state['include_reviews_checkbox']
    st.session_state['include_photo_captioning_checkbox'] = st.session_state['include_photo_captioning_checkbox']
    st.session_state['kml_download_option'] = st.session_state['kml_download_option']


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    persist_state()