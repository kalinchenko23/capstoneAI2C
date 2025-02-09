import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
import json


def download_button(object_to_download, download_filename):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # Try JSON encode for everything else
    else:
        object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:text/csv;base64,{b64}" download="{download_filename}">')[0].click()
    </script>
    </head>
    </html>
    """
    return dl_link


def download_df():
    df = pd.DataFrame(st.session_state.col_values, columns=[st.session_state.col_name])
    components.html(
        download_button(df, st.session_state.filename),
        height=0,
    )


with st.form("my_form", clear_on_submit=False):
    st.text_input("Column name", help="Name of column", key="col_name")
    st.multiselect(
        "Entries", options=["A", "B", "C"], help="Entries in column", key="col_values"
    )
    st.text_input("Filename (must include .csv)", key="filename")
    submit = st.form_submit_button("Download dataframe", on_click=download_df)