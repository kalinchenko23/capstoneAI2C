import streamlit as st

from helpers.validation_helper_functions import validate_location, validate_search_radius, validate_user_id, validate_token
from helpers.generate_map import generate_map, scroll_to_top_of_map

# This is displayed on the tab that the application is opened in
# other options for app icon = 🛠️ 🧰
st.set_page_config(
   page_title="Tactical OPE Toolkit", 
   page_icon="🧰",
)

# st.header('Tactical OPE Toolkit')

# imports and reads the "styles.css file"
with open('./styles/styles.css') as f:
    st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)

# initializing a state variable that will track if all inputs have been validated
if 'inputs_validated' not in st.session_state:
    st.session_state['inputs_validated'] = False

# initializing a state variable that will track if the map is being displayed (and therefore a query can be submitted)
if 'map_displayed' not in st.session_state:
    st.session_state['map_displayed'] = False

# initializing a state variable that will track if a query has been submitted
if 'query_submitted' not in st.session_state:
    st.session_state['query_submitted'] = False

def reset_inputs():
    st.session_state['inputs_validated'] = False
    st.session_state['map_displayed'] = False

#=========================================================================================================================
with st.container(border=True):
    # This creates a 1row x 2column "grid" that the input boxes are sitting in
    user_id_column, token_column = st.columns(2)

# This creates a 1row x 2column "grid" that the input boxes are sitting in
location_column, location_type_column = st.columns(2)

# This creates a 1row x 2column "grid" that the input boxes are sitting in
search_radius_column, search_radius_units_column = st.columns(2)

# creates the "user_id" input field
user_id = user_id_column.text_input(
    'user-id', 
    value="", 
    max_chars=None, 
    key='user-id', 
    type="default", 
    help=None, 
    autocomplete=None, 
    on_change=reset_inputs, 
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
    type='default', 
    help=None, 
    autocomplete=None, 
    on_change=reset_inputs, 
    placeholder='token', 
    disabled=False, 
    label_visibility="collapsed"
    )

# creates the "location" input field
location = location_column.text_input(
    'location', 
    value="", 
    max_chars=None, 
    key='location_input', 
    type='default', 
    help=None, 
    autocomplete=None, 
    on_change=reset_inputs, 
    placeholder=None, 
    disabled=False, 
    label_visibility="visible"
    )

# creates the location "type" drop down select box adjacent to the "location" textbox
location_type = location_type_column.selectbox(
    label='type', 
    # options=['Lat/Lon', 'MGRS', 'DMS'],
    options=['Lat/Lon', 'MGRS', 'Address'],
    index=0, 
    # format_func=special_internal_function, 
    key='location_type', 
    help=None, 
    on_change=reset_inputs, 
    placeholder="Choose an option", 
    disabled=False, 
    # label_visibility="visible"
    label_visibility="hidden"
    )

# creates the "search radius" input field
search_radius = search_radius_column.text_input(
    'search radius', 
    value="", 
    max_chars=None, 
    key='radius_input', 
    type="default", 
    help=None, 
    autocomplete=None, 
    on_change=reset_inputs, 
    placeholder='', 
    disabled=False, 
    label_visibility="visible"
    )

# creates the "units" drop down select box adjacent to the "search radius" textbox
search_radius_units = search_radius_units_column.selectbox(
    label='units', 
    options=['Meters', 'Feet'], 
    index=0, 
    # format_func=special_internal_function, 
    key='radius_units', 
    help=None, 
    on_change=reset_inputs, 
    placeholder="Choose an option", 
    disabled=False, 
    # label_visibility="visible"
    label_visibility="hidden"
    )
#=========================================================================================================================

# on "validate", validate the required fields
validation_button = st.button(
'validate', 
key='validate_button', 
help=None, 
on_click=None, 
type="secondary", 
icon=None, 
disabled=False, 
use_container_width=False
)

if validation_button: # triggered when the validation button is pressed
    validated_location = validate_location(location, location_type)
    validated_search_radius = validate_search_radius(search_radius, search_radius_units)
    # something something 'included types'
    validated_user_id = validate_user_id(user_id)
    validated_token = validate_token(token)

    # toggling the state variable that is tracking validation of user inputs
    # this will be used to determine wether we show the validation map or not
    if validated_location and validated_search_radius and validated_user_id and validated_token:
        st.session_state['inputs_validated'] = True
        st.session_state['validated_location'] = validated_location
        st.session_state['validated_search_radius'] = validated_search_radius
        st.session_state['validated_user_id'] = validated_user_id
        st.session_state['validated_token'] = validated_token
        st.session_state['query_submitted'] = False
    else:
        st.session_state['inputs_validated'] = False

# if the inputs are validated, display validation map to user
if st.session_state['inputs_validated'] == True:
    validation_map = generate_map(st.session_state['validated_location'], st.session_state['validated_search_radius'])
    scroll_to_top_of_map()
    st.session_state['map_displayed'] = True
else:
    st.session_state['map_displayed'] = False

# if the map is currently being displayed, allow users to either "submit" or "cancel" their query
if st.session_state['map_displayed'] == True:
    
    # This creates a 1row x 2column "grid" that the buttons are sitting in
    cancel_button_column, submit_button_column = st.columns(2)

    # cancel button
    cancel_button = cancel_button_column.button(
    'cancel', 
    key='cancel_button', 
    help=None, 
    on_click=None, 
    type="secondary", 
    icon=None, 
    disabled=False, 
    use_container_width=False
    )

    # when the cancel button is clicked
    if cancel_button:
        reset_inputs()
        st.rerun()

    # submit button
    submit_button = submit_button_column.button(
    'submit', 
    key='submit_button',  
    type="secondary",  
    disabled=False, 
    use_container_width=False
    )

    # when the submit button is clicked
    if submit_button:
        st.session_state['query_submitted'] = True
        reset_inputs()
        st.rerun()

if st.session_state['query_submitted'] == True:
    request_body = {
        'lat': float(st.session_state['validated_location'][0]), 
        'lon': float(st.session_state['validated_location'][1]), 
        'rad': float(st.session_state['validated_search_radius']), 
        'includedTypes': [], 
        'user_id': str(st.session_state['validated_user_id']), 
        'token': str(st.session_state['validated_token'])
    }

    st.write('post request to "/search_nearby" endpoint')
    st.write(request_body)

        
# st.write(st.session_state)

# TODO: 
# function
# figure out form download
# wierd thing where '4QFJ1144557789asdf' is still converted properly...
# feedback button with pocs (see anchorman repo)
# 'included types' shenanigans
# kmz download option
# the map takes a while to load the first time the app is launched...

# style
# hide/show password for 'token' field, will likely need to bring my own svg for displaying
# cancel and submit button styling
# do we need classification / warning banner (see anchorman repo)

# misc
# scrape the shit out of the image ids for google places

