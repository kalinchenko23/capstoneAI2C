import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import Draw
from branca.element import Template, MacroElement
import math

from styles.icons.icons import pin_icon, bounding_box_icon, trashcan_icon

from components.validation_functions import validate_location

def generate_map():
    # create the map
    m = folium.Map(location=(39, 34), 
                   zoom_start=st.session_state['map_zoom_level'], 
                   attr= st.session_state['dummy_string_for_map_rerendering'],
                   min_zoom=2, 
                   min_lat=-90, 
                   min_lon=-180,
                   max_lat=90,
                   max_lon=180,
                   max_bounds=True
                   )
    
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

def calculate_zoom_based_on_bbox_size(bounds):
    # !!! this is an approximation and should NOT be taken as super accurate
    (lat_min, lon_min), (lat_max, lon_max) = bounds

    # Mean latitude for adjusting longitude distance
    mean_lat = math.radians((lat_min + lat_max) / 2)

    # Approximate degrees to kilometers
    lat_km = 111.32
    lon_km = 111.32 * math.cos(mean_lat)

    # Height and width in km
    height_km = abs(lat_max - lat_min) * lat_km
    width_km = abs(lon_max - lon_min) * lon_km

    approx_area = height_km * width_km # area in km^2

    # long logic chain that is determining the zoom level based on the size of the box
    if approx_area < 0.0005:
        st.session_state['map_zoom_level'] = 19
    elif approx_area < 0.003:
        st.session_state['map_zoom_level'] = 18
    elif approx_area < 0.01:
        st.session_state['map_zoom_level'] = 17
    elif approx_area < 0.05:
        st.session_state['map_zoom_level'] = 16
    elif approx_area < 0.8:
        st.session_state['map_zoom_level'] = 15
    elif approx_area < 1.0:
        st.session_state['map_zoom_level'] = 14
    elif approx_area < 20:
        st.session_state['map_zoom_level'] = 13
    elif approx_area < 50:
        st.session_state['map_zoom_level'] = 12
    elif approx_area < 100:
        st.session_state['map_zoom_level'] = 11
    elif approx_area < 500:
        st.session_state['map_zoom_level'] = 10
    elif approx_area < 2_000:
        st.session_state['map_zoom_level'] = 9
    elif approx_area < 10_000:
        st.session_state['map_zoom_level'] = 8
    elif approx_area < 100_000:
        st.session_state['map_zoom_level'] = 7
    elif approx_area < 700_000:
        st.session_state['map_zoom_level'] = 6
    elif approx_area < 2_000_000:
        st.session_state['map_zoom_level'] = 5
    elif approx_area < 8_000_000:
        st.session_state['map_zoom_level'] = 4
    elif approx_area < 16_000_000:
        st.session_state['map_zoom_level'] = 3
    else:
        st.session_state['map_zoom_level'] = 2

def force_map_rerender_cb(caller=''):
    # this is adding a space to one of the state variables that are used to generate the map at the top of the file;
    # by changing this value, the map rerenders

    if caller == 'delete_boxes':
        # ensure there are boxes on the map, this prevents the map rerendering when delete is clicked if nothings on the map
        if len(st.session_state['rectangle_feature_group']._children) > 1:
            st.session_state['dummy_string_for_map_rerendering'] = st.session_state['dummy_string_for_map_rerendering'] + ' '
    else:
        st.session_state['dummy_string_for_map_rerendering'] = st.session_state['dummy_string_for_map_rerendering'] + ' '

def reset_price_prediction():
    # this resets the price prediction state variables if the bounding box changes
    st.session_state['price_predicted'] = False
    st.session_state['price_prediction'] = {}

    # this resets the query submitted and duplicate query warning state variable if the bounding box changes
    st.session_state['query_submitted'] = False
    st.session_state['duplicate_query_warning_displayed'] = False
    

def search_area():
    m = generate_map()
    
    with st.container(key='map_container'):
        col1, col2 = st.columns(2)

        with col1.popover(pin_icon, help='Add Pin'):
            location_input_column, add_pin_column = st.columns(2)

            location = location_input_column.text_input(
                'location', 
                value='', 
                key='location_input', 
                placeholder='lat, lon', 
                label_visibility='collapsed'
            )

            if add_pin_column.button('Add Pin', key='add_pin_button'):
                    st.session_state['location_validation_results'] = validate_location(location)

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

                            force_map_rerender_cb()
        
        if col1.button(trashcan_icon, help='Delete Pins'):
            st.session_state['points_feature_group'] = folium.FeatureGroup('points')
                    

        with col1.popover(bounding_box_icon, help='Add Bounding Box'):
            coord_column, add_box_col = st.columns(2)

            sw_coord = coord_column.text_input(
                'sw coordinate', 
                value='', 
                key='sw_coord',  
                placeholder='sw coordinate', 
                label_visibility="collapsed"
            )

            ne_coord = coord_column.text_input(
                'ne coordinate', 
                value='', 
                key='ne_coord',  
                placeholder='ne coordinate', 
                label_visibility="collapsed"
            )

            with st.container(key='box_controls'):
                if add_box_col.button('Add Bounding Box', key='draw_box_button'):
                    st.session_state['validated_sw_coord'] = validate_location(sw_coord)
                    st.session_state['validated_ne_coord'] = validate_location(ne_coord)

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

                            # this resets the price prediction state variables if a new bounding box is drawn
                            reset_price_prediction()

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

        if col1.button(trashcan_icon, help='Delete Bounding Boxes', on_click=force_map_rerender_cb, args=('delete_boxes', )):
            st.session_state['rectangle_feature_group']._children.clear() # removing all shapes from rectangle feature group
            st.session_state['map']['last_active_drawing'] = []
            st.session_state['user_bounding_box'] = None

            # this resets the price prediction state variables if the bounding boxes are deleted
            reset_price_prediction()
            
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

                # handle centering on dropped/drawn box
                st.session_state['map_center'] = calculate_center_of_bbox(bounds)

                # dynamically determine how far to zoom based on the size of the box
                calculate_zoom_based_on_bbox_size(bounds)
                
                # Prevent duplicate rectangles
                already_exists = any(
                    isinstance(child, folium.Rectangle) and bounds == child.locations
                    for child in st.session_state['rectangle_feature_group']._children.values()
                )

                if st.session_state['user_bounding_box'] != st.session_state['map']['last_active_drawing']:
                    reset_price_prediction()

                for child in st.session_state['rectangle_feature_group']._children.values():
                    if isinstance(child, folium.Rectangle):
                        coords = shape_data['geometry']['coordinates']
                        bounds = [[coords[0][0][1], coords[0][0][0]], [coords[0][2][1], coords[0][2][0]]]

                        if child.get_bounds() == bounds:
                            child.options['color'] = 'red'
                            child.options['fillColor'] = 'blue'
                            st.session_state['user_bounding_box'] = st.session_state['map']['last_active_drawing']
                        else:
                            child.options['color'] = 'blue'
     
                # drawing our box to the map
                if not already_exists:
                    folium.Rectangle(
                        bounds=bounds, 
                        color='blue', 
                        fill=True).add_to(st.session_state['rectangle_feature_group']) 
                    
                    force_map_rerender_cb()
                    
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

        with col2.container():
            st_folium(m, 
                    zoom=st.session_state['map_zoom_level'], 
                    center=st.session_state['map_center'],
                    feature_group_to_add=[st.session_state['points_feature_group'], st.session_state['rectangle_feature_group']],
                    width=1020, height=510, key='map', use_container_width=False, returned_objects=['last_active_drawing', 'zoom', 'center'])
            

if __name__ == "__main__":
    generate_map()
    check_for_duplicate_pins()
    check_for_duplicate_boxes()
    calculate_center_of_bbox()
    calculate_zoom_based_on_bbox_size()
    force_map_rerender_cb()
    reset_price_prediction()
    search_area()