# newest version

import streamlit as st

from icons.icons import toolbox_icon
from components.initialize_state import initialize_state
from components.user_credentials import show_user_credentials
from components.search_area import show_search_area
from components.query_options import show_query_options
from components.review_query import review_and_submit_query
from components.establishment_search import establishment_search

from components.auto_scroller import scroll_to_top_of_map

st.set_page_config(
   page_title="Tactical OPE Toolkit", 
   page_icon=toolbox_icon,
   layout="wide"
)

initialize_state()

def test_callback():
    if st.session_state['navbar'] == 'User Credentials':
        scroll_to_top_of_map()

with st.sidebar:
    st.subheader('Tactical OPE Toolkit')   
    st.radio("Navigation", ['User Credentials', 'Search Area', 'Query Options', 'Review + Submit'], label_visibility='collapsed', key='navbar', on_change=test_callback)
    # st.write(st.session_state)
    
st.subheader('User Credentials')
show_user_credentials()
st.divider() 

st.subheader('Search Area')
establishment_search()
show_search_area()
st.divider() 

st.subheader('Query Options')
show_query_options()
st.divider() 

st.subheader('Review + Submit')
review_and_submit_query()

