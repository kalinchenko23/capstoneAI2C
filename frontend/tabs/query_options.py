import streamlit as st

# TODO:
# big info box

@st.fragment
def query_options():
    # creates the "select output fields" containers and pills
    with st.container(border=True, key='select_output_fields_container'):
        st.write('Select the Data Included in Output')

        # sentences displayed when a user hovers over the corresponding '?' 
        # need to do something in the styling to differentiate the help text box from the background
        basic_data_help = '''
        This includes the place:
        - name
        - address
        - location (lat/lon)
        - phone number
        - website url 
        - reviews
        - hours of operation
        - photos'''
        review_summarization_help = 'Selecting this option will trigger AI to summarize the reviews for each location.'
        photo_captioning_help = 'Selecting this option will trigger AI to caption all available photos from each location.'

        # triggered when the 'All' checkbox is selected; automatically selects/deselects the other checkboxes
        def update_states_all_selected():
            if st.session_state['all_fields_checkbox']:
                st.session_state['include_reviews_checkbox'] = True
                st.session_state['include_photo_captioning_checkbox'] = True
            else:
                st.session_state['include_reviews_checkbox'] = False
                st.session_state['include_photo_captioning_checkbox'] = False

        # this forces the 'Basic Data' checkbox to always be True
        def update_states_basic_selected():
            st.session_state['basic_data_checkbox'] = True

        # all chekbox
        st.checkbox(label='All', 
                    key='all_fields_checkbox',  
                    on_change=update_states_all_selected)

        with st.container(border=True):
            # basic data chekbox
            st.checkbox(label='Basic Data', 
                        key='basic_data_checkbox', 
                        help=basic_data_help, 
                        on_change=update_states_basic_selected
                        )

            # ai review summary checkbox
            st.checkbox(label='Include AI Review Summarization',  
                        key='include_reviews_checkbox', 
                        help=review_summarization_help, 
                        )

        
            # ai photo captions checkbox
            st.checkbox(label='Include AI Photo Captioning',  
                        key='include_photo_captioning_checkbox', 
                        help=photo_captioning_help, 
                        )

            # if 'include ai photo captioning' is selected, creates the text input field
            if st.session_state['include_photo_captioning_checkbox']:
                with st.container(border=True, key='image_analysis_container'):
                    vlm_input = st.text_input(
                        label='Enter Keywords for AI to Highlight (leave blank for generic image captioning)', 
                        value="", 
                        max_chars=None, 
                        key='vlm_input', 
                        type='default',
                        help='''
                        Enter key words you would like AI to target. (max 150 characters)\n
                        Examples: cameras, windows, security\n
                        *Leave blank for general image captioning
                        ''', 
                        autocomplete=None, 
                        on_change=None, 
                        placeholder='Examples: cameras, windows, security', 
                        disabled=False, 
                        label_visibility="visible"
                    )

    # creates the kml/kmz toggle
    st.toggle(
        'Include KMZ Download', 
        key='kml_download_option', 
        help=None, 
        on_change=None, 
        disabled=False, 
        label_visibility="visible"
    )

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    query_options()
