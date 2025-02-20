from streamlit.components.v1 import html
import time

# not 100% sure how this thing works but it does so....
# when a user clicks "User Credentials", the entire page scrolls so that section is the focus
def scroll_to_top_of_map():
    html('''
    <script>
        // Time of creation of this script = {now}.
        // The time changes everytime and hence would force streamlit to execute JS function
        function scrollToMySection() {{
            var element = window.parent.document.querySelector('[class="stVerticalBlock st-key-map-container st-emotion-cache-1o3oenk eiemyj3"]');
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

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    scroll_to_top_of_map()


# var element = window.parent.document.getElementById("st-key-map_container");
# let inputElement = document.querySelector('[class="stVerticalBlock st-key-map-container st-emotion-cache-1o3oenk eiemyj3"]')