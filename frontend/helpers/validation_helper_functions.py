import streamlit as st
import mgrs

# icon used in all of the st.warnings
icon="⚠️"


def validate_location(location, location_type):
    # first ensure that a value has been input for the "location" input field
    if len(location.strip()) == 0:
        st.warning('location field can not be empty', icon=icon)

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
                st.warning(f'Invalid MGRS - "{location}"\n', icon=icon)


        elif location_type == 'Lat/Lon':
            try:
                # checking to see if input location are comma seperated or not
                if ',' in location:
                    lat_str, lon_str = location.split(",")
                else:
                    lat_str, lon_str = location.split(" ")
            
            except ValueError:
                st.warning("""
                            Invalid location format\n
                            Please enter coordinates in one of the following valid formats:
                            
                            - Latitude, Longitude (e.g., 21.318604, -157.9254212)
                            - Latitude,Longitude (e.g., 21.318604,-157.9254212)
                            - Latitude Longitude (e.g., 21.318604 -157.9254212)
                          """, icon=icon)
                return

                
            try:
                # checking to see if the latitude can be converted to a float and that its value is legitimate
                dd_lat = float(lat_str.strip())

                if not (-90 <= dd_lat <= 90):
                    raise ValueError

            except ValueError:
                st.warning(f"""
                            Invalid latitude - "{lat_str}"\n
                            Please ensure that latitude is between -90 and 90
                            """, icon=icon)
                return
                    

            try:
                # checking to see if the longitude can be converted to a float and that its value is legitimate
                dd_lon = float(lon_str.strip())

                if not (-180 <= dd_lon <= 180):
                    raise ValueError

            except ValueError: # happens when lon cant be casted to a float
                st.warning(f"""
                            Invalid longitude - "{lon_str}"\n
                            Please ensure that longitude is between -180 and 180
                            """, icon=icon)
                return 
                    

            return (dd_lat, dd_lon)   


        elif location_type == 'Address':
            # have to handle geocoding with geocoding api, might be more expensive but will surely be more accurate
            st.write('address selected - TODO')

def validate_search_radius(search_radius, search_radius_units):
    # ensure that a value has been input for the "search radius" input field
    if len(search_radius.strip()) == 0:
        st.warning('search radius field can not be empty', icon=icon)

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
            st.warning('Please enter a valid search radius (number between 1 and 5000)', icon=icon)

def validate_user_id(user_id):
    if len(user_id.strip()) == 0:
        st.warning('user-id field can not be empty', icon=icon) 
    else:
        return user_id     

def validate_token(token):
    if len(token.strip()) == 0:
        st.warning('token field can not be empty', icon=icon) 
    else:
        return token 
    