# -24.76716, 133.592090
# user bbox: 14.108807, 24.4347374 | 43.336315, 77.1691130
# user bbox2: -14.445651, -14.911131 | 29.678209, 33.604494

# TODO:
# currently, there is only one 'type' selector, all coords on the tab are using that 'type' for validation
# style for the whole tab:
    # error messages kinda look wonky
    # not in love with scrolling up and down to drop pins/boxes and look at the map
# test the shit out of the bbox coords to ensure the one highlighted in red is the one reflected in the query

import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import Draw
from branca.element import Template, MacroElement

from components.validation_functions import validate_location

def generate_map():
    # create the map
    m = folium.Map(location=st.session_state['location_validation_results'], zoom_start=st.session_state['map_zoom_level'], min_zoom=2, max_bounds=True)

    # Add the legend with the modified template
    legend_template = """
    {% macro html(this, kwargs) %}
    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.5);
        border-radius: 6px; padding: 10px; font-size: 12px; left: 15px; bottom: 35px;'>     
        <div class='legend-scale'>
        <ul class='legend-labels'>
            <li><span style='background-color: lightblue; border: 2px solid red; opacity: 0.75;'></span>Box Used For Query</li>
            <li><span style='background-color: lightblue; border: 2px solid blue; opacity: 0.75;'></span>Inactive Bounding Box</li>
        </ul>
        </div>
    </div> 
    <style type='text/css'>
    .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
    .maplegend .legend-scale ul li {list-style: none; line-height: 22px; margin-bottom: 1.5px;}
    .maplegend ul.legend-labels li span {float: left; height: 16px; width: 16px; margin-right: 4.5px; border-radius: 3px;}
    </style>
    {% endmacro %}
    """

    # Create the macro element
    macro = MacroElement()
    macro._template = Template(legend_template)

    # Add the legend to the map
    m.get_root().add_child(macro)

    return m

def check_for_duplicate_pins(coords):
    # value returned at end after comparison
    already_exists = False

    # convert coords to a list for the comparison
    coords = [coords[0], coords[1]]

    # if the box already exists, set already_exists to True
    for child in st.session_state['points_feature_group']._children.values():
        if isinstance(child, folium.Marker):
            child_coords = child.get_bounds()[0]

            if coords == child_coords:
                already_exists = True
                break

    return already_exists

def check_for_duplicate_boxes(bounds):
    # value returned at end after comparison
    already_exists = False

    # Convert bounds to a list of lists for the comparison
    bounds = [list(bound) for bound in bounds]

    # if the box already exists, set already_exists to True
    for child in st.session_state['rectangle_feature_group']._children.values():
            if isinstance(child, folium.Rectangle):
                child_bounds = child.get_bounds()

                if bounds == child_bounds:
                    already_exists = True
                    break

    return already_exists

def calculate_center_of_bbox(bounds): # this enables 'snapping' to a bbox
    # Extract latitudes and longitudes from the bounds
    lat_min, lon_min = bounds[0]  # Southwest corner (lat_min, lon_min)
    lat_max, lon_max = bounds[1]  # Northeast corner (lat_max, lon_max)
    
    # Calculate the center of the bounding box
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    
    return (center_lat, center_lon)

def force_map_rerender(m):
    # Creating an invisible marker and adding it directly to the map
    # this causes the map to rerender and gets rid of any boxes in folium's default feature group
    invisible_icon = folium.Icon(icon='circle', icon_size=(0,0), shadow_size=(0,0))
    folium.Marker(location=(0,0), icon=invisible_icon).add_to(m)

# this is causing an issue if the tabs are changed too fast by the user
@st.fragment
def search_area():
    m = generate_map()
    
    with st.container(border=True, key='map-container'):
        
        with st.container(border=True):
            location_column, location_type_column = st.columns(2)

            location = location_column.text_input(
                'location', 
                value='', 
                key='location_input', 
                placeholder='location', 
                label_visibility='collapsed'
            )

            location_type = location_type_column.selectbox(
                label='type', 
                options=['Lat/Lon'],
                index=0, 
                key='location_type', 
                placeholder='Choose an option', 
                label_visibility='collapsed'
            )

            with st.container(key='pin_controls'):
                if st.button('Add Pin', key='add_pin_button'):
                    st.session_state['location_validation_results'] = validate_location(location, location_type)

                    # ensure the coordinates are validated
                    if st.session_state['location_validation_results']:

                        # Check for duplicates and create the pin if it doesn't already exist
                        if not check_for_duplicate_pins(st.session_state['location_validation_results']):
                            folium.Marker(
                                location=st.session_state['location_validation_results'],
                                popup=st.session_state['location_validation_results'], 
                                icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
                            ).add_to(st.session_state['points_feature_group'])

                            # edit the "last_active_drawing" in session state to reflect the new pin
                            lat = st.session_state['location_validation_results'][0]
                            lon = st.session_state['location_validation_results'][1]

                            new_pin = {
                                        "type": "Feature",
                                        "properties": {},
                                        "geometry": {
                                            "type": "Point",
                                            "coordinates": [
                                                lon,
                                                lat
                                            ]
                                        }
                                    }

                            st.session_state['map']['last_active_drawing'] = new_pin
                            force_map_rerender(m)

                if st.button('Delete Pins'):
                    st.session_state['points_feature_group'] = folium.FeatureGroup('points')
                    
                    

        with st.container(border=True):
            sw_coord_column, ne_coord_column = st.columns(2)

            sw_coord = sw_coord_column.text_input(
                'sw coordinate', 
                value='', 
                key='sw_coord',  
                placeholder='sw coordinate', 
                label_visibility="collapsed"
            )

            ne_coord = ne_coord_column.text_input(
                'ne coordinate', 
                value='', 
                key='ne_coord',  
                placeholder='ne coordinate', 
                label_visibility="collapsed"
            )

            with st.container(key='box_controls'):
                if st.button('Add Bounding Box', key='draw_box_button'):
                    st.session_state['validated_sw_coord'] = validate_location(sw_coord, location_type)
                    st.session_state['validated_ne_coord'] = validate_location(ne_coord, location_type)

                    # ensure the input coordinates are valid
                    if st.session_state['validated_sw_coord'] and st.session_state['validated_ne_coord']:
                        # Get the southwest and northeast coordinates
                        sw_lat, sw_lon = st.session_state['validated_sw_coord']
                        ne_lat, ne_lon = st.session_state['validated_ne_coord']

                        # Ensure that the SW coordinates have lower lat/lon and NE coordinates have higher lat/lon
                        lat_min = min(sw_lat, ne_lat)
                        lat_max = max(sw_lat, ne_lat)
                        lon_min = min(sw_lon, ne_lon)
                        lon_max = max(sw_lon, ne_lon)

                        # create the bounds with the corrected coordinates
                        bounds = [(lat_min, lon_min), (lat_max, lon_max)]

                        # Check for duplicates and create the rectangle if it doesn't already exist
                        if not check_for_duplicate_boxes(bounds):
                            folium.Rectangle(
                                bounds=bounds, 
                                color='red', 
                                fill=True, 
                                fillColor='blue'
                            ).add_to(st.session_state['rectangle_feature_group'])

                            # Store the last active drawing as the new bounding box
                            new_bounding_box = {
                                "type": "Feature",
                                "properties": {},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [[lon_min, lat_min], [lon_min, lat_max], [lon_max, lat_max], [lon_max, lat_min], [lon_min, lat_min]]
                                    ]
                                }
                            }
                            
                            st.session_state['map']['last_active_drawing'] = new_bounding_box
                            force_map_rerender(m)


                if st.button('Delete Boxes', key='delete_box_button'):
                    st.session_state['rectangle_feature_group']._children.clear() # removing all shapes from rectangle feature group
                    st.session_state['map']['last_active_drawing'] = []
                    st.session_state['user_bounding_box'] = None

                    force_map_rerender(m)

                    # because the map is rerendering, we need to maintain the maps current zoom level and center
                    # without doing this, the map snaps back to the center and zoom level of the last box
                    current_center_lat = st.session_state['map']['center']['lat']
                    current_center_lon = st.session_state['map']['center']['lng']
                    st.session_state['map_center'] = (current_center_lat, current_center_lon)
                    st.session_state['map_zoom_level'] = st.session_state['map']['zoom']

        # Handle new drawings from the user
        if 'map' in st.session_state and st.session_state['map']['last_active_drawing']:
            shape_data = st.session_state['map']['last_active_drawing']

            # handle zooming to dropped pins
            if shape_data['geometry']['type'] == 'Point':
                lat = shape_data['geometry']['coordinates'][1]
                lon = shape_data['geometry']['coordinates'][0]

                st.session_state['map_center'] = (lat, lon)
                st.session_state['map_zoom_level'] = 13
            

            # handle bounding boxes
            if shape_data['geometry']['type'] == 'Polygon':

                coords = shape_data['geometry']['coordinates']
                bounds = [[coords[0][0][1], coords[0][0][0]], [coords[0][2][1], coords[0][2][0]]]

                # handle zooming to dropped/drawn box
                st.session_state['map_center'] = calculate_center_of_bbox(bounds)
                st.session_state['map_zoom_level'] = 13

                # Prevent duplicate rectangles
                already_exists = any(
                    isinstance(child, folium.Rectangle) and bounds == child.locations
                    for child in st.session_state['rectangle_feature_group']._children.values()
                )

                for child in st.session_state['rectangle_feature_group']._children.values():
                    if isinstance(child, folium.Rectangle):
                        coords = shape_data['geometry']['coordinates']
                        bounds = [[coords[0][0][1], coords[0][0][0]], [coords[0][2][1], coords[0][2][0]]]

                        if child.get_bounds() == bounds:
                            # st.write(f'{child} is active')
                            child.options['color'] = 'red'
                            child.options['fillColor'] = 'blue'
                            st.session_state['user_bounding_box'] = st.session_state['map']['last_active_drawing']
                        else:
                            # st.write(f'{child} is not active')
                            child.options['color'] = 'blue'
                        
                if not already_exists:
                    folium.Rectangle(
                        bounds=bounds, 
                        color='blue', 
                        fill=True
                    ).add_to(st.session_state['rectangle_feature_group']) 

        # Updated draw options to disable unwanted tools
        draw_options = {
            'polyline': False, 
            'polygon': False,
            'circle': False, 
            'circlemarker': False, 
            'marker': False,
            'rectangle': True  # Only allow rectangle drawing
        }

        edit_options = {
            'edit': False,  # Disable editing of existing features
            'remove': False  # Disable built-in delete (trash can)
        }

        Draw(draw_options=draw_options, edit_options=edit_options).add_to(m)

        st_folium(m, 
                  zoom=st.session_state['map_zoom_level'], 
                  center=st.session_state['map_center'],

                  feature_group_to_add=[st.session_state['points_feature_group'], st.session_state['rectangle_feature_group']],
                  width=600, height=500, key='map', use_container_width=True, returned_objects=['last_active_drawing', 'zoom', 'center'])
        
        
        force_map_rerender(m)

if __name__ == "__main__":
    generate_map()
    check_for_duplicate_pins()
    check_for_duplicate_boxes()
    calculate_center_of_bbox()
    force_map_rerender()
    search_area()
