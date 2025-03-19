from streamlit.components.v1 import html
import time

# not 100% sure how this thing works but it does so....
# when a user clicks "Drop Pin", the entire page scrolls to that container
# WARNING: If you alter the containers or order of elements on the "Search Area" tab you might break how this is targeting
# if you need to do that, and cant figure this out: it might be best to completely remove this auto scrolling all together (its not critical, just a perk)
def scroll_to_top_of_map():
    html('''
    <script>
        // Time of creation of this script = {now}.
        // The time changes everytime and hence would force streamlit to execute JS function
        function scrollToMySection() {{
            var element = window.parent.document.querySelectorAll('[class="st-emotion-cache-4uzi61 eiemyj5"]')[1];
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


# def scroll_to_top_of_submit():
#     html('''
#     <script>
#         // Time of creation of this script = {now}.
#         // The time changes everytime and hence would force streamlit to execute JS function
#         function scrollToMySection() {{
#             var element = window.parent.document.querySelector('[class="stVerticalBlock st-key-review-container st-emotion-cache-1o3oenk eiemyj3"]');
#             if (element) {{
#                 element.scrollIntoView({{ behavior: "smooth", block: "start" }});
#             }} else {{
#                 setTimeout(scrollToMySection, 100);
#             }}
#         }}
#         scrollToMySection();
#     </script>
#     '''.format(now=time.time(), tab_id="<your-tab-id>"
#     ))

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    scroll_to_top_of_map()
    # scroll_to_top_of_submit()
