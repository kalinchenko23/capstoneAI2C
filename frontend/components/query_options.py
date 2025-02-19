import streamlit as st

# TODO:
# big info box
# explanation of the fields in the field select help 
# breakout field selection into "tiers" based on pricing from the google maps api

def show_query_options():
    # creates the "select output fields" containers and pills
    with st.container(border=True, key='select_output_fields_container'):
        st.write('Select the Data Included in Output')

        def update_states_all_selected():
            if st.session_state['all_fields_checkbox']:
                st.session_state['basic_data_checkbox'] = True
                st.session_state['include_reviews_checkbox'] = True
                st.session_state['include_photo_captioning_checkbox'] = True
            else:
                st.session_state['basic_data_checkbox'] = True
                st.session_state['include_reviews_checkbox'] = False
                st.session_state['include_photo_captioning_checkbox'] = False

        def update_states_basic_selected():
            st.session_state['basic_data_checkbox'] = True

        # so the real question is... do we want users to be able to ever do a query that DOESNT return the 'Basic Data'
        def update_states_reviews_or_captions_seclected():
            if st.session_state['include_reviews_checkbox'] or st.session_state['include_photo_captioning_checkbox']:
                st.session_state['basic_data_checkbox'] = True
        
        st.checkbox(label='All', value=False, key='all_fields_checkbox', help='test', on_change=update_states_all_selected)

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

        
        with st.container(border=True):

            # basic data chekbox
            st.checkbox(label='Basic Data', 
                        # value=True if st.session_state['all_fields_checkbox'] else False, 
                        value=True,
                        # disabled=True, 
                        key='basic_data_checkbox', 
                        help=basic_data_help, 
                        on_change=update_states_basic_selected)

        # ai review summary checkbox
            st.checkbox(label='Include AI Review Summarization', 
                        value=True if st.session_state['all_fields_checkbox'] else False, 
                        key='include_reviews_checkbox', 
                        help=review_summarization_help, 
                        on_change=update_states_reviews_or_captions_seclected)

        
        # ai photo captions checkbox
            st.checkbox(label='Include AI Photo Captioning', 
                        value=True if st.session_state['all_fields_checkbox'] else False, 
                        key='include_photo_captioning_checkbox', 
                        help=photo_captioning_help, 
                        on_change=update_states_reviews_or_captions_seclected)

            if st.session_state['include_photo_captioning_checkbox']:
                # creates the "image_analysis_input" text input
                with st.container(border=True, key='image_analysis_container'):
                    vlm_input = st.text_input(
                        label='Enter Keywords for AI to Highlight (leave blank for generic image captioning)', 
                        value="", 
                        max_chars=None, 
                        key='image_analysis_input', 
                        type='default',
                        help='''
                        Enter key words you would like AI to target.\n
                        Examples: "cameras", "windows", "security"\n
                        *Leave blank for general image captioning
                        ''', 
                        autocomplete=None, 
                        on_change=None, 
                        placeholder='Examples: "cameras", "windows", "security"', 
                        disabled=False, 
                        label_visibility="visible"
                    )

    # creates the kml/kmz toggle
    st.toggle(
        'Include KML/KMZ Download', 
        value=False, 
        key='kml_download_option', 
        help=None, 
        on_change=None, 
        disabled=False, 
        label_visibility="visible"
    )

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    show_query_options()