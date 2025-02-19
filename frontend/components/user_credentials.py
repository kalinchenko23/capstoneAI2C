import streamlit as st

def show_user_credentials():
    with st.container(border=True):
        # This creates a 1row x 2column "grid" that the input boxes are sitting in
        user_id_column, token_column = st.columns(2)

    # creates the "user_id" input field
    user_id = user_id_column.text_input(
        'user-id', 
        value="", 
        max_chars=None, 
        key='user_id', 
        type="default", 
        help=None, 
        autocomplete=None, 
        on_change=None, 
        placeholder='user-id', 
        disabled=False, 
        label_visibility="collapsed"
    )

    # creates the "token" input field
    token = token_column.text_input(
        'token', 
        value="", 
        max_chars=None, 
        key='token_input', 
        type='password',  # hides the user input
        help=None, 
        autocomplete=None, 
        on_change=None, 
        placeholder='token', 
        disabled=False, 
        label_visibility="collapsed"
    )

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    show_user_credentials()
