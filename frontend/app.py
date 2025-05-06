import streamlit as st

from styles.icons.icons import toolbox_icon
from state_management.initialize_state import initialize_state
from tabs.create_tabs import create_tabs
from tabs.search_area import search_area
from tabs.query_options import query_options
from tabs.review_and_submit import review_and_submit

st.set_page_config(
page_title="PLAID", 
page_icon=toolbox_icon,
layout="wide"
)

# Display app name in upper left corner
st.markdown('<h3>PL<span style="color:red;">AI</span>DE</h3>', unsafe_allow_html=True)

# initialize state variables used throughout the application
initialize_state()

# imports and reads the "styles.css" file
with open('./styles/styles.css') as f:
      st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)

# Display app name in upper left corner
st.markdown('<h3>PL<span style="color:red;">AI</span>D</h3>', unsafe_allow_html=True)

# define the tabs you want displayed
active_tab = create_tabs(['Search Area', 'Query Options', 'Review + Submit'])

# checking and conditionally rendering based on what tab is selected
if st.session_state['active_tab'] == 'Search Area':
      search_area()
elif st.session_state['active_tab'] == 'Query Options':
      query_options()
elif st.session_state['active_tab'] == 'Review + Submit':
      review_and_submit()