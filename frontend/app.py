import streamlit as st

from styles.icons.icons import toolbox_icon
from state_management.initialize_state import initialize_state
from tabs.establishment_search import establishment_search
from tabs.search_area import search_area
from tabs.query_options import query_options
from tabs.review_and_submit import review_and_submit


st.set_page_config(
page_title="PLAIDE", 
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


st.header('Search Area', anchor=False, divider="gray")
establishment_search() 
search_area()
st.header('Query Options', anchor=False, divider="gray")
query_options()
st.header('Review + Submit', anchor=False, divider="gray")
review_and_submit()
