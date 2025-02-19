from streamlit.components.v1 import html
import time

# not 100% sure how this thing works but it does so....
# when a user clicks "validate" and a map is generated, the entire page scrolls down so the map is the focus
def scroll_to_top_of_map(target):
    html('''
    <script>
        // Time of creation of this script = {now}.
        // The time changes everytime and hence would force streamlit to execute JS function
        function scrollToMySection() {{
            var element = window.parent.document.getElementById("user-credentials");
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
