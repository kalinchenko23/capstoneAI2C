import streamlit as st
import pandas as pd

from components.cost_estimator import mock_cost_estimator

# TODO:
# big info box

@st.fragment
def query_options():
    test_col_1, test_col_2 = st.columns(2)

    # creates the "select output fields" containers and pills
    with test_col_1.container(border=True, key='select_output_fields_container'):
        col_1, col_2, col_3 = st.columns(3) # this is just an easy way to move the toggle further to the right
        col_1.write('Select the Data Included in Output')
        # creates the kmz toggle
        col_3.toggle(
            'Include KMZ Download', 
            key='kmz_download_option', 
            help=None, 
            on_change=None, 
            disabled=False, 
            label_visibility="visible"
        )

        # sentences displayed when a user hovers over the corresponding '?' 
        # need to do something in the styling to differentiate the help text box from the background
        basic_data_help = '''
        This includes the place:
        - name
        - address
        - location (lat/lon)
        - phone number
        - website url 
        - reviews
        - hours of operation
        - photos'''
        review_summarization_help = 'Selecting this option will trigger AI to summarize the reviews for each location.'
        photo_captioning_help = 'Selecting this option will trigger AI to caption all available photos from each location.'

        # triggered when the 'All' checkbox is selected; automatically selects/deselects the other checkboxes
        def update_states_all_selected():
            if st.session_state['all_fields_checkbox']:
                st.session_state['include_reviews_checkbox'] = True
                st.session_state['include_photo_captioning_checkbox'] = True
            else:
                st.session_state['include_reviews_checkbox'] = False
                st.session_state['include_photo_captioning_checkbox'] = False

        # this forces the 'Basic Data' checkbox to always be True
        def update_states_basic_selected():
            st.session_state['basic_data_checkbox'] = True

        # all chekbox
        st.checkbox(label='All', 
                    key='all_fields_checkbox',  
                    on_change=update_states_all_selected)
        

        # basic data chekbox
        with st.container(border=True):
            basic_col_1, basic_col_2 = st.columns(2)
            
            basic_col_1.checkbox(label='Basic Data', 
                        key='basic_data_checkbox', 
                        help=basic_data_help, 
                        on_change=update_states_basic_selected
                        )
            
            # creates the text input field for google maps api key
            if st.session_state['basic_data_checkbox']:
                    basic_col_2.text_input(
                        label='Google Maps API Key:', 
                        value="", 
                        key='google_maps_api_key', 
                        type='password',   
                        placeholder='Google Maps API Key:',  
                        label_visibility="collapsed"
                    )







        # ai review summary checkbox
        with st.container(border=True):
            review_col_1, review_col_2 = st.columns(2)

            review_col_1.checkbox(label='Include AI Review Summarization',  
                        key='include_reviews_checkbox', 
                        help=review_summarization_help, 
                        )
            
            # if 'include ai review summarization' is selected, creates the text input field for the llm key
            if st.session_state['include_reviews_checkbox']:
                review_col_2.text_input(
                    label='OpenAI LLM Key:', 
                    value="", 
                    key='llm_key', 
                    type='password',   
                    placeholder='Open AI LLM Key:',  
                    label_visibility="collapsed"
                )

        with st.container(border=True):
            photo_col_1, photo_col_2 = st.columns(2)
        
            # ai photo captions checkbox
            photo_col_1.checkbox(label='Include AI Photo Captioning',  
                        key='include_photo_captioning_checkbox', 
                        help=photo_captioning_help, 
                        )

            # if 'include ai photo captioning' is selected, creates the text input field
            if st.session_state['include_photo_captioning_checkbox']:
                photo_col_2.text_input(
                    label='OpenAI VLM Key:', 
                    value="", 
                    key='vlm_key', 
                    type='password',   
                    placeholder='Open AI VLM Key:',  
                    label_visibility="collapsed"
                )

                with st.container(border=True, key='image_analysis_container'):
                    st.text_input(
                        label='Enter Keywords for AI to Highlight (leave blank for generic image captioning)', 
                        value="", 
                        max_chars=None, 
                        key='vlm_input', 
                        type='default',
                        help='''
                        Enter key words you would like AI to target. (max 150 characters)\n
                        Examples: cameras, windows, security\n
                        *Leave blank for general image captioning
                        ''', 
                        autocomplete=None, 
                        on_change=None, 
                        placeholder='Examples: cameras, windows, security', 
                        disabled=False, 
                        label_visibility="visible"
                    )

    # beginning of cost prediction stuff
    
    with test_col_2.container(border=True):
        # st.write(st.session_state['price_prediction'])
        # st.write(st.session_state['price_predicted'])

        if st.session_state['price_predicted'] == False:

            precondtions_prompt = ('In order to make a prediction you must provide:\n'
                                    '1. Establishment Search Term\n'
                                    '2. Search Area Bounding Box\n'
                                    '3. Google Maps API Key'
                                    )
            
            prediction_cost_prompt = "Predicting the cost will incur a charge between 3 and 9 cents."

            # three conditions need to be met for the price prediction button to be enabled
            predict_cost_preconditions = bool(st.session_state['establishment_search_input'] and 
                                         st.session_state['user_bounding_box'] and 
                                         st.session_state['google_maps_api_key'])
            
            if st.button('Predict Query Time and Cost', 
                            help=prediction_cost_prompt if predict_cost_preconditions else precondtions_prompt, 
                            on_click=None, 
                            type="secondary", 
                            disabled=False if predict_cost_preconditions else True, 
                            use_container_width=True):
                
                mock_cost_estimator()
                st.session_state['price_predicted'] = True
                st.rerun(scope='fragment')
            
            table_data = [
                            {"Tier": "Basic",  "Time": "--",  "Cost": "--"},
                            {"Tier": "Review", "Time": "--",  "Cost": "--"},
                            {"Tier": "Photo",  "Time": "--",  "Cost": "--"},
                            {"Tier": "All",    "Time": "--",  "Cost": "--"}
                        ]
            
            df = pd.DataFrame(table_data)
            df.reset_index(drop=True)
            st.write('establishments found: -')
            st.table(df)
            
        
        elif st.session_state['price_predicted'] == True:
            st.button('Predict Query Time and Cost', 
                        help="Price already predicted for current search term and search area",  
                        type="secondary", 
                        disabled=True, 
                        use_container_width=True)
            
            data = st.session_state['price_prediction']
            table_data = [
                            {"Tier": "Basic",  "Time": data["basic_time"],      "Cost": data["basic_cost"]},
                            {"Tier": "Review", "Time": data["reviews_time"],    "Cost": data["reviews_cost"]},
                            {"Tier": "Photo",  "Time": data["photos_time"],     "Cost": data["photos_cost"]},
                            {"Tier": "All",    "Time": data["time_everything"], "Cost": data["cost_everything"]}
                        ]
            df = pd.DataFrame(table_data)
            df.reset_index(drop=True)

            # Round all numeric values (except for "couple of seconds", which is a string)
            df["Cost"] = df["Cost"].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
            df["Time"] = df["Time"].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
            
            # Display without index
            st.write(f'establishments found: {data["places"]}')
            st.table(df)

            # set state variable tracking if a prediction has been generated
            st.session_state['price_predicted'] = True

            # get the sums of currently selected tiers to display to the user
            total_prediction = st.session_state['price_prediction']
            time_prediction = 0
            cost_prediction = 0

            if st.session_state['basic_data_checkbox']:
                time_prediction += total_prediction['basic_time']
                cost_prediction += total_prediction['basic_cost']
            if st.session_state['include_reviews_checkbox']:
                time_prediction += total_prediction['reviews_time']
                cost_prediction += total_prediction['reviews_cost']
            if st.session_state['include_photo_captioning_checkbox']:
                time_prediction += total_prediction['photos_time']
                cost_prediction += total_prediction['photos_cost']
            
            time_prediction = round(time_prediction, 2)
            cost_prediction = round(cost_prediction, 2)

            prediction_totals_col_1, prediction_totals_col_2 = st.columns(2)

            prediction_totals_col_1.write(f'Predicted Query Time: {time_prediction}')
            prediction_totals_col_2.write(f'Predicted Query Cost: {cost_prediction}')
            




            
    


# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    query_options()
