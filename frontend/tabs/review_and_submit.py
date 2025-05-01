import streamlit as st

from styles.icons.icons import warning_icon, terminated_query_warning
from components.validation_functions import validate_vlm_key, validate_llm_key, validate_establishment_search, validate_bounding_box, validate_google_maps_api_key, validate_photo_caption_keywords
from components.post_request_and_download import text_search_post_request

# this is a popup that is displayed once after a valid query, 
# it is part of the workflow that disables the submit button until various things are changed
@st.dialog('Duplicate Query')
def duplicate_query_warning_popup():
    duplicate_query_warning = ('Your current query is identical to your previous query. In order to submit a new one, you must change at least one of the following:\n'
                                '1. Establishment Search Term\n'
                                '2. Search Area Bounding Box\n'
                                '3. Output File types\n'
                                '4. Requested Data Tiers\n'
                                '5. Required API Keys\n'
                                )
    
    st.warning(duplicate_query_warning, icon=warning_icon)
    
    st.session_state['duplicate_query_warning_displayed'] = True


# I am using this as a way to stop the user from interacting with input widgets while the query is being processed
# if the user closes this popup window the process ends
@st.dialog('Query In Progress')
def submit_dialog_popup(validated_establishment_search,
                                         validated_bounding_box,
                                         validated_photo_caption_keywords,
                                         validated_google_maps_api_key,
                                         validated_llm_key, 
                                         validated_vlm_key, 
                                         bbox_tuples):
    
    st.warning('**Exiting this window while a query is being processed will result in the termination of the query.**', icon=terminated_query_warning)

    with st.spinner():
                text_search_post_request(validated_establishment_search,
                                         validated_bounding_box,
                                         validated_photo_caption_keywords,
                                         st.session_state['requested_tiers'],
                                         validated_google_maps_api_key,
                                         validated_llm_key, 
                                         validated_vlm_key, 
                                         bbox_tuples)
                
def review_and_submit():
    # display warning for the user
    
    # st.warning('Submitting a query **will** incur a cost for your organization based on the query options you have selected.', 
    #             icon=warning_icon)
    
    with st.container(border=True, key='review-submit-container'):
        inputs_column, outputs_column = st.columns(2)
        
        # determine which 'tiers' of data are being requested 
        # this string is displayed in the review section
        requested_results = ''

        if st.session_state['basic_data_checkbox']:
            requested_results += 'Basic Admin data'
        if st.session_state['include_reviews_checkbox']:
            requested_results += ', Review Summaries'
        if st.session_state['include_photo_captioning_checkbox']:
            requested_results += ', Photo Captions'

        # display the users 'vlm input', keywords to be passed to the vlm for photo captions
        photo_captions_target_phrase = ''
        if st.session_state['vlm_input'].strip() == "":
            photo_captions_target_phrase = 'None'
        else:
            photo_captions_target_phrase = f"{st.session_state['vlm_input']}"

        # get the input bounding box coords to display to the user
        if st.session_state['user_bounding_box']:
            coords = st.session_state['user_bounding_box']['geometry']['coordinates']
            ne_coord = (coords[0][2][1], coords[0][2][0])
            sw_coord = (coords[0][0][1], coords[0][0][0])
        else:
            ne_coord = ''
            sw_coord = ''

        # Creates the review container
        with st.container(border=True, key='review-container'):
            inputs_column.markdown(f"""  
            **Searching for:** `{st.session_state['establishment_search_input'] or "None"}`  
            """)

            inputs_column.markdown(f"""
            **Bounding Box:**  
            """)

            if sw_coord and ne_coord:
                inputs_column.code(f"SW: {sw_coord}\nNE: {ne_coord}")
            else:
                inputs_column.markdown("`None`")

            inputs_column.markdown(f"""
            **Photo Captions Keywords:** `{photo_captions_target_phrase}`  
            """)

            outputs_column.markdown(f"""  
            **Results Will Include:** `{requested_results if requested_results else "No data selected"}`

            **Include KMZ Download:** `{"Yes" if st.session_state['kmz_download_option'] else "No"}` 

            **Include JSON Download:** `{"Yes" if st.session_state['json_download_option'] else "No"}`
            """)

            if st.session_state['price_predicted']:
                outputs_column.markdown(f"""
                **Predicted Time:** `{st.session_state['predicted_time']}`

                **Predicted Cost:** `{st.session_state['predicted_cost']}`
                """)
          
    # this state var is instantiated as False and changes to True when the submit button is clicked
    if st.session_state['query_submitted'] == False: 

        # try to validate required inputs
        validated_establishment_search = validate_establishment_search(st.session_state['establishment_search_input'])
        validated_bounding_box = validate_bounding_box(st.session_state['user_bounding_box'])
        validated_photo_caption_keywords = validate_photo_caption_keywords(st.session_state['vlm_input'])
        validated_google_maps_api_key = validate_google_maps_api_key(st.session_state['google_maps_api_key'])
        validated_llm_key = validate_llm_key(st.session_state['llm_key'])
        validated_vlm_key = validate_vlm_key(st.session_state['vlm_key'])

        # all of these conditions need to be met for the submit button to be enabled
        submit_query_preconditions = bool(
            validated_establishment_search and
            validated_bounding_box and
            validated_photo_caption_keywords is not None and # checking for None here becuase an empty string is valid in this case
            validated_google_maps_api_key and
            validated_llm_key is not None and # checking for None here becuase an empty string is valid in this case
            validated_vlm_key is not None) # checking for None here becuase an empty string is valid in this case
        
        # prompt thats used before a query has been submitted if any of these havent been provided 
        precondtions_prompt = ('In order to submit a query you must provide:\n'
                                '1. Establishment Search Term\n'
                                '2. Search Area Bounding Box\n'
                                '3. Required API Keys'
                                )

        # if the button is clicked, call the submit_dialog_popup function (which then calls the post_request_and_download function)
        if st.button(
            'Submit',
            key='submit_button', 
            help=None if submit_query_preconditions else precondtions_prompt, # determines which prompt to display 
            type="secondary", 
            disabled=False if submit_query_preconditions else True,
            use_container_width=False):

            # convert validated bbox to required data structure for kmz
            bbox_tuples = [tuple(item) for item in validated_bounding_box['geometry']['coordinates'][0]]
            
            submit_dialog_popup(validated_establishment_search,
                                         validated_bounding_box,
                                         validated_photo_caption_keywords,
                                         validated_google_maps_api_key,
                                         validated_llm_key, 
                                         validated_vlm_key, 
                                         bbox_tuples)

    # if the button has been pressed and the user already submitted the identical query, disable the button
    elif st.session_state['query_submitted'] == True:
        st.button(
            'Submit',
            key='submit_button', 
            help='Identical query already submitted', 
            type='secondary', 
            disabled=True,
            use_container_width=False)
        
        if not st.session_state['duplicate_query_warning_displayed']:
            duplicate_query_warning_popup()
                
# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    review_and_submit()