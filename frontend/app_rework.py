import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw 
import requests


#################################################################################################################
# st.info('info')
# st.warning('warning')
# st.error('error')

st.set_page_config(
   page_title="Tactical OPE Toolkit", 
   page_icon="🧰",
#    layout="wide"
)

# # imports and reads the "styles.css file"
# with open('./styles/light-styles.css') as f:
#     st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)


# st.subheader('Tactical OPE Toolkit')
#################################################################################################################

#################################################################################################################
with st.sidebar:
    st.radio(
    "Navigation",
    ['user credentials', 'bounding box', 'build query', 'review query', 'submit'],

    # captions=[
    #     "Laugh out loud.",
    #     "Get the popcorn.",
    #     "Never stop learning.",
    # ],
)
    
#################################################################################################################

#################################################################################################################
st.subheader('User Credentials')
with st.container(border=True):
    # This creates a 1row x 2column "grid" that the input boxes are sitting in
    user_id_column, token_column = st.columns(2)

# creates the "user_id" input field
user_id = user_id_column.text_input(
    'user-id', 
    value="", 
    max_chars=None, 
    key='user-id', 
    type="default", 
    help=None, 
    autocomplete=None, 
    on_change=None, 
    placeholder='user-id', 
    disabled=False, 
    label_visibility="collapsed"
    )

# creates the "token" input field
token = token_column.text_input(
    'token', 
    value="", 
    max_chars=None, 
    key='token_input', 
    type='password',  # hides the user input
    help=None, 
    autocomplete=None, 
    on_change=None, 
    placeholder='token', 
    disabled=False, 
    label_visibility="collapsed"
    )
#################################################################################################################

#################################################################################################################
st.subheader('Bounding Box')
with st.container(border=True):
# This creates a 1row x 2column "grid" that the input boxes are sitting in
    southwest_coordinate_column, northeast_coordinate_column = st.columns(2)


    st.write('Draw a polygon to get bounding box coordinates.')
    # Create a map centered at a specific location
    m = folium.Map(location=[15.721049, 47.4529562], zoom_start=5)

    # Add the drawing tool to the map
    draw = Draw(export=False)
    m.add_child(draw)

    # Display the map in Streamlit
    # !!! for some reason, adding the 'key' param to st_folium is causing a duplication in the st.session_state
    #     however, the original key is dynamically named and I don't want to risk not targeting it correctly.
    #     So I am opting to leave the 'map' key in, as I can ensure that I can target that state object
    output = st_folium(m, key='map', use_container_width=True, height=350)

    # Check if anything was drawn


    if output and "last_active_drawing" in output:
        # st.write(output)
        drawing = output["last_active_drawing"]
        if drawing and drawing["geometry"]["type"] == "Polygon":
            # Extract coordinates of the bounding box
            coordinates = drawing["geometry"]["coordinates"][0]
            min_lat = min(coord[1] for coord in coordinates)
            max_lat = max(coord[1] for coord in coordinates)
            min_lon = min(coord[0] for coord in coordinates)
            max_lon = max(coord[0] for coord in coordinates)  

# logic for handling the interactivity of inputting coords vs drawing a box
# if 'map' in st.session_state:
# still fucked
if st.session_state['map']['last_active_drawing'] == None:
    sw_value = ''
    ne_value = ''
    label_visibility = 'hidden'
else:
    sw_value = f'{min_lat}, {min_lon}'
    ne_value = f'{max_lat}, {max_lon}'
    label_visibility = 'visible'


southwest_coordinate = southwest_coordinate_column.text_input(
    'southwest coordinate', 
    value=sw_value, 
    max_chars=None, 
    key='sw_coord', 
    type="default", 
    help=None, 
    autocomplete=None, 
    on_change=None, 
    placeholder='southwest coordinate (lat, lon)', 
    disabled=False, 
    label_visibility=label_visibility
    )

# creates the ne corner input field
northeast_coordinate = northeast_coordinate_column.text_input(
    'northeast coordinate', 
    value=ne_value, 
    max_chars=None, 
    key='ne_coord', 
    type='default',
    help=None, 
    autocomplete=None, 
    on_change=None, 
    placeholder='northeast coordinate (lat, lon)', 
    disabled=False, 
    label_visibility=label_visibility
    )
#################################################################################################################

#################################################################################################################
st.subheader('Build Query')
# creates the "text query" input field
with st.container(border=True):
    establishment_query = st.text_input(
        label='Establishment Search', 
        value="", 
        max_chars=None, 
        key='text_query_input', 
        type='default',
        help='''
        Enter as if you were using Google Maps on your phone.\n
        Examples: "food", "hotels", "gas station"
        ''', 
        autocomplete=None, 
        on_change=None, 
        placeholder='Examples: "food", "hotels", "gas station"', 
        disabled=False, 
        label_visibility="visible"
    )


    #need to enable the all button
    def all_check():
        if 'All' in field_selection:
            pass

    raw_options = ['All', 'name', 'website', 'phone number', 'address', 'latitude', 'longitude', 'reviews', 
                'photos', 'street_view', 'working hours', 'image captioning', 'review summarization'
                ]

    options = sorted(raw_options)

    field_selection = st.pills(
        "Fields", 
        options,
        selection_mode="multi", 
        default=None, 
        format_func=None, 
        key='fieldmask_input', 
        help=None, 
        on_change=None,  
        disabled=False, 
        label_visibility="visible")

    # st.markdown(f"Fields that will be returned: {field_selection}.")

    vlm_input = st.text_input(
        label='Image Analysis', 
        value="", 
        max_chars=None, 
        key='vlm_input', 
        type='default',
        help='''
        Enter key words you would like AI to target.\n
        Examples: "cameras", "windows", "security"\n
        Leave blank for general image captioning
        ''', 
        autocomplete=None, 
        on_change=None, 
        placeholder='Examples: "cameras", "windows", "security"', 
        disabled=False, 
        label_visibility="visible"
    )

    st.toggle(
        'Include KML/KMZ Download', 
        value=False, 
        key=None, 
        help=None, 
        on_change=None, 
        disabled=False, 
        label_visibility="visible"
    )

#################################################################################################################

#################################################################################################################
# submit button
submit_button = st.button(
'submit', 
key='submit_button', 
help=None, 
on_click=None, 
type="secondary", 
icon=None, 
disabled=False, 
use_container_width=False, 
)




# st.write(st.session_state['map'])



request_body = {
    "text_query": "", 
    "lat_sw": 1234.56, 
    "lng_sw": 1234.56,
    "lat_ne": 1234.56,
    "lng_ne": 1234.56,
    "user_id": "user123",
    "token": "290aa941a27675013735d287d1fc5ebe16983a8dd08937819f"
}