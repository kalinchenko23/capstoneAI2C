
import streamlit as st
import folium
from branca.element import Template, MacroElement
from folium.plugins import Draw
from streamlit_folium import st_folium

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

@st.fragment
def search_area():
    # container 1
    with st.container(border=True, key='map-container'):

        # container 2
        with st.container():
            shapes_column, map_column = st.columns(2)

            # container 3a
            with shapes_column.container():
                location_column, location_type_column = st.columns(2)
                add_pin_column, delete_pins_column = st.columns(2)

                # pin location input
                location = location_column.text_input(
                'location', 
                value='', 
                key='location_input', 
                placeholder='location', 
                label_visibility='collapsed'
                )

                # location type input
                location_type = location_type_column.selectbox(
                label='type', 
                options=['Lat/Lon', 'MGRS', 'Address'],
                index=0, 
                key='location_type', 
                placeholder='Choose an option', 
                label_visibility='collapsed'
                )

                # add pin button
                if add_pin_column.button('Add Pin', key='add_pin_button'):
                    pass

                # delete pins button
                if delete_pins_column.button('Delete Pins'):
                    pass

            # container 3b        
            with shapes_column.container():
                sw_coord_column, ne_coord_column = st.columns(2)
                add_box_column, delete_boxes_column = st.columns(2)

                # sw coordinate input
                sw_coord = sw_coord_column.text_input(
                'sw coordinate', 
                value='', 
                key='sw_coord',  
                placeholder='sw coordinate', 
                label_visibility="collapsed"
                )

                # ne coordinate input
                ne_coord = ne_coord_column.text_input(
                    'ne coordinate', 
                    value='', 
                    key='ne_coord',  
                    placeholder='ne coordinate', 
                    label_visibility="collapsed"
                )

                # add box button
                if add_box_column.button('Add Bounding Box', key='draw_box_button'):
                    pass

                # delete boxes button
                if delete_boxes_column.button('Delete Boxes', key='delete_box_button'):
                    pass


            # container 4
            # with map_column.container():
            with st.container():
                m = generate_map()

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
                    width=600, height=300, key='map', use_container_width=True, returned_objects=['last_active_drawing', 'zoom', 'center'])
                

if __name__ == "__main__":
    search_area()
    generate_map()

            











