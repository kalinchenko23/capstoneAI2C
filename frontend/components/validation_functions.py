import streamlit as st

from styles.icons.icons import validation_error_icon

def validate_location(location, location_type):
    # first ensure that a value has been input for the "location" input field
    if len(location.strip()) == 0:
        st.error('location field can not be empty', icon=validation_error_icon)

    else:
        
        if location_type == 'Lat/Lon':
            try:
                # checking to see if input location are comma seperated or not
                if ',' in location:
                    lat_str, lon_str = location.split(",")
                else:
                    lat_str, lon_str = location.split(" ")
            
            except ValueError:
                st.error("""
                            Invalid location format\n
                            Please enter coordinates in one of the following valid formats:
                            
                            - 21.318604, -157.9254212
                            - 21.318604,-157.9254212
                            - 21.318604 -157.9254212
                          """, icon=validation_error_icon)
                return

                
            try:
                # checking to see if the latitude can be converted to a float and that its value is legitimate
                dd_lat = float(lat_str.strip())

                if not (-90 <= dd_lat <= 90):
                    raise ValueError

            except ValueError:
                st.error(f"""
                            Invalid latitude - "{lat_str}"\n
                            Please ensure that latitude is between -90 and 90
                            """, icon=validation_error_icon)
                return
                    

            try:
                # checking to see if the longitude can be converted to a float and that its value is legitimate
                dd_lon = float(lon_str.strip())

                if not (-180 <= dd_lon <= 180):
                    raise ValueError

            except ValueError: # happens when lon cant be casted to a float
                st.error(f"""
                            Invalid longitude - "{lon_str}"\n
                            Please ensure that longitude is between -180 and 180
                            """, icon=validation_error_icon)
                return 
                    

            return (dd_lat, dd_lon)   

def validate_search_radius(search_radius, search_radius_units):
    # ensure that a value has been input for the "search radius" input field
    if len(search_radius.strip()) == 0:
        st.error('search radius field can not be empty', icon=validation_error_icon)

    else:
        try:
            # ensure that the 'search_radius' input can be converted to a float
            search_radius_number = float(search_radius)

            # check if conversion to meters is necessary (the google maps api requires meters)
            if search_radius_units == 'Feet':
                # arbitrarily decided to round this down to two digits
                search_radius_number = round(search_radius_number / 3.281, 2)

            # ensure the search radius is a positive number that does not exceed 5000 meters
            if search_radius_number <= 0 or search_radius_number > 5000:
                raise ValueError
            else:
                return search_radius_number
            
        except ValueError:
            st.error('Please enter a valid search radius (number between 1 and 5000)', icon=validation_error_icon)

def validate_google_maps_api_key(google_maps_api_key):
    if len(google_maps_api_key) == 0:
        st.error('google maps api key field can not be empty', icon=validation_error_icon) 
    else:
        return google_maps_api_key

def validate_llm_key(llm_key):
    if st.session_state['include_reviews_checkbox']: # if the key is required
        if len(llm_key) == 0: # display an error if an empty key has been provided
            st.error('llm key field can not be empty if review summarization is selected', icon=validation_error_icon) 
            return None
        else: # some non empty key has been provided
            return llm_key
    else: # if the key is not required, return an empty string (this is passed to the post request)
        return '' 
    
def validate_vlm_key(vlm_key):
    if st.session_state['include_photo_captioning_checkbox']: # if the key is required
        if len(vlm_key) == 0: # display an error if an empty key has been provided
            st.error('vlm key field can not be empty if photo captioning is selected', icon=validation_error_icon) 
            return None
        else: # some non empty key has been provided
            return vlm_key
    else:
        return '' # if the key is not required, return an empty string (this is passed to the post request)

def validate_establishment_search(establishment_search_input):
    if len(establishment_search_input.strip()) == 0:
        st.error('establishment search field can not be empty', icon=validation_error_icon) 
    else:
        return establishment_search_input 
    
def validate_bounding_box(user_bounding_box):
    # check for none, throw error
    if not user_bounding_box:
        st.error('You must provide a valid search area', icon=validation_error_icon)
    # ensure its a rectangle, if not throw error
    elif user_bounding_box['geometry']['type'] != 'Polygon':
        st.error('An unexpected error occured. Please navigate back to search area tab and click the bounding box you would like to query', icon=validation_error_icon)
    else:
        return user_bounding_box
    
def validate_photo_caption_keywords(vlm_input):
    if len(vlm_input) > 150:
        st.error('photo caption keywords can not exceed 150 characters', icon=validation_error_icon)
    else:
        return vlm_input
    
# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    validate_location()
    validate_search_radius()
    validate_google_maps_api_key()
    validate_establishment_search()
    validate_bounding_box()
    validate_photo_caption_keywords()
    validate_llm_key()
    