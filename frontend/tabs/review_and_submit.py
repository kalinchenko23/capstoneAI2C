import streamlit as st

from styles.icons.icons import warning_icon
from components.validation_functions import validate_vlm_key, validate_llm_key, validate_establishment_search, validate_bounding_box, validate_google_maps_api_key, validate_photo_caption_keywords

from components.post_request_and_download import text_search_post_request

# TODO:
# when error messages display, they are all stacked up at the bottom. Could probably be done better

@st.fragment
def review_and_submit():
    # display warning for the user
    
    st.warning('Submitting a query **will** incur a cost for your organization based on the query options you have selected.', 
                icon=warning_icon)
    
    with st.container(border=True, key='review-submit-container'):
        inputs_column, outputs_column = st.columns(2)
        
        # determine which 'tiers' of data are being requested 

        # this string is used to generate the review section
        requested_results = ''
        # this list is going to be passed to the actual post request. (Ex: ["reviews", "photos"])
        requested_tiers = []
        if st.session_state['basic_data_checkbox']:
            requested_results += 'Basic Admin data'
        if st.session_state['include_reviews_checkbox']:
            requested_results += ', Review Summaries'
            requested_tiers.append('reviews')
        if st.session_state['include_photo_captioning_checkbox']:
            requested_results += ', Photo Captions'
            requested_tiers.append('photos')

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
            """)

            outputs_column.markdown(f"""
            **Predicted Time:** `{st.session_state['predicted_time']}`

            **Predicted Cost:** `{st.session_state['predicted_cost']}`
            """)
        
    # submit button
    submit_button = st.button(
    'submit', 
    key='submit_button', 
    help=None, 
    on_click=None, 
    type="secondary", 
    icon=None, 
    disabled=False, 
    use_container_width=False, 
    )

    # upon submit, validate user inputs based on specific requirements
    if submit_button:
        validated_establishment_search = validate_establishment_search(st.session_state['establishment_search_input'])
        validated_bounding_box = validate_bounding_box(st.session_state['user_bounding_box'])
        validated_photo_caption_keywords = validate_photo_caption_keywords(st.session_state['vlm_input'])
        validated_google_maps_api_key = validate_google_maps_api_key(st.session_state['google_maps_api_key'])
        validated_llm_key = validate_llm_key(st.session_state['llm_key'])
        validated_vlm_key = validate_vlm_key(st.session_state['vlm_key'])

        # if all required fields pass validation
        if (
            validated_establishment_search and
            validated_bounding_box and
            validated_photo_caption_keywords is not None and # checking for None here becuase an empty string is valid in this case
            validated_google_maps_api_key and
            validated_llm_key is not None and # checking for None here becuase an empty string is valid in this case
            validated_vlm_key is not None # checking for None here becuase an empty string is valid in this case
           ): 
            
            # convert validated bbox to required data structure for kmz
            bbox_tuples = [tuple(item) for item in validated_bounding_box['geometry']['coordinates'][0]]

            # make the post request with a spinner
            with st.spinner():
                text_search_post_request(validated_establishment_search,
                                         validated_bounding_box,
                                         validated_photo_caption_keywords,
                                         requested_tiers,
                                         validated_google_maps_api_key,
                                         validated_llm_key, 
                                         validated_vlm_key, 
                                         bbox_tuples)
                
# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    review_and_submit()
