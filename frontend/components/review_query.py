import streamlit as st

from icons.icons import warning_icon
from .validation_helper_functions import validate_user_id, validate_token, validate_establishment_search, validate_bounding_box
from .post_request_and_download import text_search_post_request

# TODO:
# build out a nice looking review for the user that highlights all of the options they have chosen

@st.fragment
def review_and_submit_query():
    #
    with st.container(border=True):
        st.warning('Submitting a query **will** incur a cost for your orginaztion based on the query options you have selected.', 
                   icon=warning_icon)
        
    # # creates the review container
    # with st.container(border=True):
    #     st.write(f'user id: {st.session_state['user_id']}')
    #     st.write(f'Searching for "{st.session_state['image_analysis_input']}" IVO {st.session_state['location_input']}')
    #     st.write(f'Results will include: Basic Admin data, Review Summaries, Photo Captions')
    #     st.write(f'Photo Captions Target Phrase: "Security Cameras"')


    # This creates a 1row x 2column "grid" that the buttons are sitting in
    review_button_column, submit_button_column = st.columns(2)
    # review button
    review_button = review_button_column.button(
    'review', 
    key='review_button', 
    help=None, 
    on_click=None, 
    type="secondary", 
    icon=None, 
    disabled=False, 
    use_container_width=False, 
    )

    # submit button
    submit_button = submit_button_column.button(
    'submit', 
    key='submit_button', 
    help=None, 
    on_click=None, 
    type="secondary", 
    icon=None, 
    disabled=False, 
    use_container_width=False, 
    )

    if review_button:
        # TODO: build out review pane
        st.write('lets review...')

    if submit_button:
        validated_user_id = validate_user_id(st.session_state['user_id'])
        validated_token = validate_token(st.session_state['token_input'])
        validated_establishment_search = validate_establishment_search(st.session_state['establishment_search_input'])
        validated_bounding_box = validate_bounding_box(st.session_state['map'])

        if validated_user_id and validated_token and validated_establishment_search and validated_bounding_box:
            # need to add a try catch block here for when you fail to touch the backend
            text_search_post_request()
        else:
            st.write('Validation Failed')

        


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    review_and_submit_query()
