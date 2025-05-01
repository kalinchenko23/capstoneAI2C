import streamlit as st

# got this off the internet
# it is a way to get around streamlit tabs not supporting conditional rendering: (https://docs.streamlit.io/develop/api-reference/layout/st.tabs)
def create_tabs(default_tabs = [], default_active_tab=0):
        if not default_tabs:
            return None
        active_tab = st.radio("required_label", default_tabs, index=default_active_tab, label_visibility='collapsed', key='active_tab')
        child = default_tabs.index(active_tab)+1
        st.markdown(""" 
            <style type="text/css">
            div[role=radiogroup] {
                border-bottom: 2px solid rgba(49, 51, 63, 0.1);
            }
            div[role=radiogroup] > label > div:first-of-type {
               display: none
            }
            div[role=radiogroup] {
                flex-direction: unset
            }
            div[role=radiogroup] label {
                padding-bottom: 0.5em;
                border-radius: 0;
                position: relative;
                top: 3px;
            }
            div[role=radiogroup] label .st-fc {
                padding-left: 0;
            }
            div[role=radiogroup] label:hover p {
                color: red;
            }
            div[role=radiogroup] label:nth-child(""" + str(child) + """) {   
                border-bottom: 2px solid rgb(255, 75, 75);
            }     
            div[role=radiogroup] label:nth-child(""" + str(child) + """) p {   
                color: rgb(255, 75, 75);
                padding-right: 0;
            }           
            </style>
        """,unsafe_allow_html=True)    
        return active_tab   

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    create_tabs()