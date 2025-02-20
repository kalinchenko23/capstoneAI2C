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

# if the user errors out the validation, all drawings are erased
# change it to allow the user to drop multi pins
# persist bounding box on tab switch
# 'Clear' Button to erase all drawings

# 15.366927651980896, 43.6001600047099
# 15.549774, 44.2484182 - shopping mall in Sana'a Yemen
# 38RPN6193537057

@st.fragment
def search_area():

    if 'location_validation_results' not in st.session_state:
        st.session_state['location_validation_results'] = [0, 0]

    if 'feature_group_to_add' not in st.session_state:
        st.session_state['feature_group_to_add'] = folium.FeatureGroup()

    if 'map_zoom_level' not in st.session_state:
        st.session_state['map_zoom_level'] = 1

    if 'persisted_bounding_box' not in st.session_state:
        st.session_state['persisted_bounding_box'] = folium.FeatureGroup()

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
        
        if st.button('Drop Pin', key='drop_pin_button'):
            st.session_state['feature_group_to_add'] = folium.FeatureGroup()
            st.session_state['location_validation_results'] = validate_location(location, location_type)
            
            if st.session_state['location_validation_results']:
                folium.Marker(location=st.session_state['location_validation_results'],popup=st.session_state['location_validation_results'], icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(st.session_state['feature_group_to_add'])
                # folium.Rectangle(bounds=[(st.session_state['persisted_bounding_box']['sw_coord']), (st.session_state['persisted_bounding_box']['ne_coord']) ]).add_to(st.session_state['feature_group_to_add'])
                st.session_state['map_zoom_level'] = 6
        
        # if st.button('Clear Pins', key='clear_map_button'):
        #     st.session_state['feature_group_to_add'] = folium.FeatureGroup()


        
        m = folium.Map(location=st.session_state['location_validation_results'], zoom_start=st.session_state['map_zoom_level'])
        draw_options = {
                'polyline': False, 
                'polygon': False,
                'circle': False, 
                'circlemarker': False, 
                'marker': False
            }
        
        # if st.session_state['map']['last_active_drawing']:
        # # if st.session_state['persisted_bounding_box']:
        #     coords = st.session_state['map']['last_active_drawing']['geometry']['coordinates']
        #     st.session_state['persisted_bounding_box'] = {
        #                                                     'sw_coord': (coords[0][0][1], coords[0][0][0]), 
        #                                                     'ne_coord': (coords[0][2][1], coords[0][2][0])
        #                                                 }

        #     folium.Rectangle(bounds=[(st.session_state['persisted_bounding_box']['sw_coord']), (st.session_state['persisted_bounding_box']['ne_coord']) ]).add_to(m)
        
        Draw(draw_options=draw_options).add_to(m)
        st_folium(m, 
                  feature_group_to_add=st.session_state['feature_group_to_add'],
                  width=600, height=350, key='map', use_container_width=True, returned_objects=['all_drawings', 'last_active_drawing'])
        

        
        

    st.write(st.session_state)
# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    search_area()
   


# 15.366927651980896, 43.6001600047099
# 38RPN6193537057



# # some way to persist the polygon on tab change...
# if st.session_state['map']['last_active_drawing']:
#     coords = st.session_state['map']['last_active_drawing']['geometry']['coordinates']
#     lat_sw = coords[0][0][1]
#     lng_sw = coords[0][0][0]
#     lat_ne = coords[0][2][1]
#     lng_ne = coords[0][2][0]

#     folium.Rectangle(bounds=[(lat_sw, lng_sw), (lat_ne, lng_ne) ]).add_to(m)
