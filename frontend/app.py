import streamlit as st
import time

from styles.icons.icons import toolbox_icon
from tabs.create_tabs import create_tabs

from tabs.user_credentials import user_credentials
from tabs.establishment_search import establishment_search
# from tabs.search_area import search_area
from tabs.dev_search_area import search_area
from tabs.query_options import query_options
from tabs.review_and_submit import review_and_submit


st.set_page_config(
   page_title="Tactical OPE Toolkit", 
   page_icon=toolbox_icon,
   layout="wide"
)

# imports and reads the "styles.css file"
with open('./styles/styles.css') as f:
    st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)

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
      