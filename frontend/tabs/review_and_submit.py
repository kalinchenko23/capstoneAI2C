import streamlit as st

from icons.icons import warning_icon
from components.validation_functions import validate_user_id, validate_token, validate_establishment_search, validate_bounding_box
from components.post_request_and_download import text_search_post_request
# from components.post_request_and_download import mock_post_request

# TODO:
# build out a nice looking review for the user that highlights all of the options they have chosen

@st.fragment
def review_and_submit():
    #
    with st.container(border=True):
        st.warning('Submitting a query **will** incur a cost for your orginaztion based on the query options you have selected.', 
                   icon=warning_icon)
        

    requested_results = ''
    if st.session_state['basic_data_checkbox']:
        requested_results += 'Basic Admin data'
    if st.session_state['include_reviews_checkbox']:
        requested_results += ', Review Summaries'
    if st.session_state['include_photo_captioning_checkbox']:
        requested_results += ', Photo Captions'

    photo_captions_target_phrase = ''
    if st.session_state['image_analysis_input'] == "":
        photo_captions_target_phrase = 'None'
    else:
        photo_captions_target_phrase = f'{st.session_state['image_analysis_input']}'



    # creates the review container
    with st.container(border=True):
        st.write('Query Review')
        st.write(f'user id: {st.session_state['user_id']}')
        st.write(f'Searching for: "{st.session_state['establishment_search_input']}" IVO ({st.session_state['location_input']})')

        st.write(f'Results will include: {requested_results}')

        st.write(f'Photo Captions Target Phrase: {photo_captions_target_phrase}')

        st.write(f'Include KMZ download: {st.session_state['kml_download_option']}')


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

    # if submit_button: # for mocking
    #     mock_post_request()

    if submit_button:
        validated_user_id = validate_user_id(st.session_state['user_id'])
        validated_token = validate_token(st.session_state['token_input'])
        validated_establishment_search = validate_establishment_search(st.session_state['establishment_search_input'])
        validated_bounding_box = validate_bounding_box(st.session_state['map'])

        if validated_user_id and validated_token and validated_establishment_search and validated_bounding_box:
            with st.spinner():
                text_search_post_request()
        else:
            st.write('Validation Failed')

        


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    review_and_submit()
