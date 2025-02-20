import streamlit as st

from icons.icons import toolbox_icon
from components.create_tabs import create_tabs
from components.user_credentials import user_credentials
from components.establishment_search import establishment_search
from components.search_area import search_area
from components.query_options import query_options
from components.review_and_submit import review_and_submit


st.set_page_config(
   page_title="Tactical OPE Toolkit", 
   page_icon=toolbox_icon,
   layout="wide"
)

st.subheader('Tactical OPE Toolkit') 

# define the tabs you want displayed
active_tab = create_tabs(['User Credentials', 'Search Area', 'Query Options', 'Review + Submit'])

# checking and conditionally rendering based on what tab is selected
if st.session_state['active_tab'] == 'User Credentials':
      user_credentials()
elif st.session_state['active_tab'] == 'Search Area':
      establishment_search()
      search_area()
elif st.session_state['active_tab'] == 'Query Options':
      query_options()
elif st.session_state['active_tab'] == 'Review + Submit':
      review_and_submit()


# st.write(st.session_state)
