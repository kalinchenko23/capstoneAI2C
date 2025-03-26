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
        






        # basic data chekbox
        with st.container(border=True):
            basic_col_1, basic_col_2 = st.columns(2)
            
            basic_col_1.checkbox(label='Basic Data', 
                        key='basic_data_checkbox', 
                        help=basic_data_help, 
                        on_change=update_states_basic_selected
                        )
            
            # creates the text input field for google maps api key
            if st.session_state['basic_data_checkbox']:
                    basic_col_2.text_input(
                        label='Google Maps API Key:', 
                        value="", 
                        key='google_maps_api_key', 
                        type='password',   
                        placeholder='Google Maps API Key:',  
                        label_visibility="collapsed"
                    )







        # ai review summary checkbox
        with st.container(border=True):
            review_col_1, review_col_2 = st.columns(2)

            review_col_1.checkbox(label='Include AI Review Summarization',  
                        key='include_reviews_checkbox', 
                        help=review_summarization_help, 
                        )
            
            # if 'include ai review summarization' is selected, creates the text input field for the llm key
            if st.session_state['include_reviews_checkbox']:
                review_col_2.text_input(
                    label='OpenAI LLM Key:', 
                    value="", 
                    key='llm_key', 
                    type='password',   
                    placeholder='Open AI LLM Key:',  
                    label_visibility="collapsed"
                )





        with st.container(border=True):
            photo_col_1, photo_col_2 = st.columns(2)
        
            # ai photo captions checkbox
            photo_col_1.checkbox(label='Include AI Photo Captioning',  
                        key='include_photo_captioning_checkbox', 
                        help=photo_captioning_help, 
                        )

            # if 'include ai photo captioning' is selected, creates the text input field
            if st.session_state['include_photo_captioning_checkbox']:
                photo_col_2.text_input(
                    label='OpenAI VLM Key:', 
                    value="", 
                    key='vlm_key', 
                    type='password',   
                    placeholder='Open AI VLM Key:',  
                    label_visibility="collapsed"
                )

                with st.container(border=True, key='image_analysis_container'):
                    st.text_input(
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

    # creates the kmz toggle
    st.toggle(
        'Include KMZ Download', 
        key='kmz_download_option', 
        help=None, 
        on_change=None, 
        disabled=False, 
        label_visibility="visible"
    )

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    query_options()
