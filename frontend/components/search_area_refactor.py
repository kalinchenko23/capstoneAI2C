import folium 
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import Draw, Geocoder

from .validation_helper_functions import validate_location
from components.auto_scroller import scroll_to_top_of_map

# TODO:
# info box articulating the need to minimize search area...
# allow polygon draws? how does the bounding box respond to that?
# auto scroller for the map

# 15.366927651980896, 43.6001600047099
# 38RPN6193537057

@st.fragment
def show_search_area():
    st.header("This is the refactor file")

    if 'location_validation_results' not in st.session_state:
        st.session_state['location_validation_results'] = None

    with st.container(border=True, key='map-container'):
        # This creates a 1row x 2column "grid" that the input boxes are sitting in
        location_column, location_type_column = st.columns(2)

        # creates the "location" input field
        location = location_column.text_input(
            'location', 
            value="", 
            max_chars=None, 
            key='location_input', 
            type='default', 
            help=None, 
            autocomplete=None, 
            on_change=None, 
            placeholder='location', 
            disabled=False, 
            label_visibility="collapsed"
            )

        # creates the location "type" drop down select box adjacent to the "location" textbox
        location_type = location_type_column.selectbox(
            label='type', 
            options=['Lat/Lon', 'MGRS', 'Address'],
            index=0, 
            key='location_type', 
            help=None, 
            on_change=None, 
            placeholder="Choose an option", 
            disabled=False, 
            label_visibility="collapsed"
            )
        
        def on_drop_pin_press():
            st.session_state['location_validation_results'] = validate_location(location, location_type)
            # scroll_to_top_of_map()

        st.button('Drop Pin', key='drop_pin_button', on_click=on_drop_pin_press)

        results = st.session_state['location_validation_results']
        if results:
            m = folium.Map(location=results, zoom_start=8)

            folium.Marker(location=results,popup=results, icon=folium.Icon(color='red', icon='crosshairs', prefix='fa'),).add_to(m)

            draw_options = {
                'polyline': False, 
                'polygon': False,
                'circle': False, 
                'circlemarker': False
            }
            Draw(draw_options=draw_options, show_geometry_on_click=True).add_to(m)
            Geocoder(provider='arcgis').add_to(m)
            
            output = st_folium(m, 
                               width=600, 
                               height=350, 
                               key='map',
                               use_container_width=True,
                               returned_objects=['all_drawings', 'last_active_drawing'] # just limits the amount of stuff returned by the map/stored in state
                               )

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    show_search_area()
   


# 15.366927651980896, 43.6001600047099
# 38RPN6193537057
