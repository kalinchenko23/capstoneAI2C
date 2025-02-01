import streamlit as st
from streamlit.components.v1 import html
import time

# not 100% sure how this thing works but it does so....
# when a user clicks "validate" and a map is generated, the entire page scrolls down so the map is the focus
def scroll_to_top_of_map():
    html('''
    <script>
        // Time of creation of this script = {now}.
        // The time changes everytime and hence would force streamlit to execute JS function
        function scrollToMySection() {{
            var element = window.parent.document.getElementById("deckgl-wrapper");
            if (element) {{
                element.scrollIntoView({{ behavior: "smooth" }});
            }} else {{
                setTimeout(scrollToMySection, 100);
            }}
        }}
        scrollToMySection();
    </script>
    '''.format(now=time.time(), tab_id="<your-tab-id>"
    ))


# kind of arbitrarily eyeballed these, can definitely change
def decide_zoom_level(validated_search_radius):
    # https://wiki.openstreetmap.org/wiki/Zoom_levels
    if validated_search_radius >=1 and validated_search_radius <= 500:
        return 13
    if validated_search_radius > 500 and validated_search_radius < 3000:
        return 12
    if validated_search_radius >= 3000:
        return 11

# creates the map chip (for user validation before submission)
def generate_map(validated_location, validated_search_radius):
    st.map(
        data=            {
            'latitude': [validated_location[0]], 
            'longitude': [validated_location[1]]
        },
        latitude='latitude',
        longitude='longitude', 
        color=None, 
        size=validated_search_radius, 
        zoom=decide_zoom_level(validated_search_radius), 
        use_container_width=True, 
        width=None, 
        height=None
        )
    
    return True
