import streamlit as st

def reset_price_estimator():
    # this resets the price prediction state variables if the establishment search term changes
    st.session_state['price_predicted'] = False
    st.session_state['price_prediction'] = {}

@st.fragment
def establishment_search():
    # creates the "establishment search" container and input field
    with st.container(border=True, key='establishment_search_container'):
        establishment_query = st.text_input(
            label='Establishment Search', 
            value="", 
            max_chars=None, 
            key='establishment_search_input', 
            type='default',
            help='''
            Enter as if you were using Google Maps on your phone.\n
            Examples: food, hotels, gas station
            ''', 
            autocomplete=None, 
            on_change=reset_price_estimator, 
            placeholder='Examples: food, hotels, gas station', 
            disabled=False, 
            label_visibility="visible"
        )

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    establishment_search()
    reset_price_estimator()