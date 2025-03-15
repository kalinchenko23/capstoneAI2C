import streamlit as st
import mgrs

from styles.icons.icons import validation_error_icon

def validate_location(location, location_type):
    # first ensure that a value has been input for the "location" input field
    if len(location.strip()) == 0:
        st.error('location field can not be empty', icon=validation_error_icon)

    else:
        # instantiting the conversion object needed for any conversions
        # might want to move this depending on wether we offer more conversions or not...
        conversion_base = mgrs.MGRS()

        if location_type == 'MGRS':
            # try to convert mgrs to dd (Lat/Lon)
            try:
                mgrs_to_dd = conversion_base.toLatLon(location)
                return mgrs_to_dd
            
            except mgrs.core.MGRSError:
                st.error(f'Invalid MGRS - "{location}"\n', icon=validation_error_icon)


        elif location_type == 'Lat/Lon':
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
                            
                            - Latitude, Longitude (e.g., 21.318604, -157.9254212)
                            - Latitude,Longitude (e.g., 21.318604,-157.9254212)
                            - Latitude Longitude (e.g., 21.318604 -157.9254212)
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


        elif location_type == 'Address':
            # have to handle geocoding with geocoding api, might be more expensive but will surely be more accurate
            st.write('address selected - TODO')

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

def validate_user_id(user_id):
    if len(user_id.strip()) == 0:
        st.error('user-id field can not be empty', icon=validation_error_icon) 
    else:
        return user_id     

def validate_token(token):
    if len(token.strip()) == 0:
        st.error('token field can not be empty', icon=validation_error_icon) 
    else:
        return token 

def validate_establishment_search(establishment_search_input):
    if len(establishment_search_input.strip()) == 0:
        st.error('establishment search field can not be empty', icon=validation_error_icon) 
    else:
        return establishment_search_input 
    
# def validate_bounding_box(map):
#     if len(map['all_drawings']) == 0 or len(map['last_active_drawing']) == 0:
#         st.error('you must provide a valid search area', icon=validation_error_icon) 
#     else:
#         return map

def validate_bounding_box(map):
    # Check if the 'last_active_drawing' is present and valid
    if not map.get('last_active_drawing'):
        st.error('You must provide a valid search area', icon=validation_error_icon)
    elif len(map['last_active_drawing']) == 0:
        st.error('You must provide a valid search area', icon=validation_error_icon)
    else:
        return map
    
def validate_photo_caption_keywords(vlm_input):
    if len(vlm_input) > 150:
        st.error('photo caption keywords can not exceed 150 characters', icon=validation_error_icon)
    

# Ensures the code runs only when this file is executed directly
if __name__ == "__main__":
    validate_location()
    validate_search_radius()
    validate_user_id()
    validate_token()
    validate_establishment_search()
    validate_bounding_box()
    validate_photo_caption_keywords()
    