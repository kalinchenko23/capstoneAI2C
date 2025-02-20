import streamlit as st

from icons.icons import toolbox_icon
from components.custom_tabs import tabs
from components.user_credentials import show_user_credentials
from components.establishment_search import establishment_search
from components.search_area import show_search_area
from components.query_options import show_query_options
from components.review_query import review_and_submit_query


st.set_page_config(
   page_title="Tactical OPE Toolkit", 
   page_icon=toolbox_icon,
   layout="wide"
)

# define the tabs you want displayed
active_tab = tabs(['User Credentials', 'Search Area', 'Query Options', 'Review + Submit'])

# checking and conditionally rendering based on what tab is selected
if st.session_state['active_tab'] == 'User Credentials':
      show_user_credentials()
elif st.session_state['active_tab'] == 'Search Area':
      establishment_search()
      show_search_area()
elif st.session_state['active_tab'] == 'Query Options':
      show_query_options()
elif st.session_state['active_tab'] == 'Review + Submit':
      review_and_submit_query()


# st.write(st.session_state)
