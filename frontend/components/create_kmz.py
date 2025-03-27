"""

This module is to get json file/raw data then extracts it to kmz

There are 8 total functions:



json_to_dict(j_file) - converts file into json 

format_hours(business_hours_list) - formats hours information to a location

get_string(data, val) - gets string data from json

get_list(data, val) - gets list data from json

get_icon(type) - gets the icon from the google (internet needed)

generalize(name) - generalizes the type based on name 

get_nw_se_coordinates(bbox_tuples) - for bounding boxes

json_to_kmz(j_file, bbox_tuples, search_term) - main function

"""

import simplekml

import json

import copy

from io import BytesIO



"""

Purpose of this function is to take j_file & turn it to dictionary

If the j_file is a path to json text, it converts to json dictionary

If the j_file is a raw jason, copy it then return the copy

"""

def json_to_dict(j_file):

    """

    Args:

        j_file (str or dict): Path to a JSON file or a dictionary object.

    Returns:

        dict: A dictionary containing the loaded JSON data.

    """

    if isinstance(j_file, str):

        with open(j_file, "r", encoding="utf-8") as file:

            dictionary = json.load(file)

    else:

        dictionary = copy.deepcopy(j_file)

    return dictionary



"""

Formats business hours as a newline-separated string.

If hours are present(list), return with lines

If hours are not present (str), returns msg "hours not available"

"""

def format_hours(business_hours_list):

    """

    Args:

        business_hours_list (list or str): Business hours in list or string format.

    Returns:

        str: Formatted business hours string.

    """

    if isinstance(business_hours_list, list):

        return "\n".join(business_hours_list)  

    else:

        return business_hours_list



"""

Safely retrieves a string value from a dictionary.

if its str - should return "not available"

if something goes wrong in dictionary returns "unavailable"

returns value of whatever key in string

"""

def get_string(data, val):

    """

    Args:

        data (dict): Dictionary to search.

        val (str): Key to retrieve the value for.

    Returns:

        str: Retrieved value as a string, or "unavailable" if not found.

    """

    try:

        answer = data[val]

        return str(answer)

    except:

        return "unavailable"



"""

Safely retrieves a list from a dictionary.

If the list is empty is will return 'unavailable'

If the something goes wrong in dictionary, returns 'unavailable'

returns values of whatver key in list

"""

def get_list(data, val):

    """

    Args:

        data (dict): Dictionary to search.

        val (str): Key to retrieve the value for.

    Returns:

        list or str: Retrieved value or "unavailable" if not found.

    """

    return data.get(val, "unavailable") if isinstance(data, dict) else "unavailable"





"""

Retrieves ICONs from google

Returns icon based on location type 

"""

def get_icon(type):

    """

    Args:

        type (str): Type of location (e.g., "restaurant", "hotel").

    Returns:

        str: URL of the icon.

    """

    icons = {

        "restaurant": "http://maps.google.com/mapfiles/kml/shapes/dining.png",

        "hotel": "http://maps.google.com/mapfiles/kml/shapes/lodging.png",

        "shopping": "http://maps.google.com/mapfiles/kml/shapes/shopping.png",

        "park": "http://maps.google.com/mapfiles/kml/shapes/parks.png",

        "default": "http://maps.google.com/mapfiles/kml/shapes/info-i.png"

    }

    return icons.get(type.lower(), icons["default"])





"""

Returns type of the location based on key names

"""

def generalize(name):

    """

    Args:

        name (str): Specific name of the location type.

    Returns:

        str: Generalized location type (e.g., "restaurant", "hotel").

    """

    types = {

        "restaurant": ("restaurant", "food", "eat", "cuisine", "cafe"),

        "hotel": ("hotel", "motel", "resort", "inn", "lodge", "cabin"),

        "shopping": ("store", "deli", "bakery", "grocery", "market"),

        "park": ("park")

    }

    for key, item in types.items():

        if name in item:

            return key

    return "default"



"""

Extracts southwest and northeast coordinates from a bounding box.

"""

def get_nw_se_coordinates(bbox_tuples):

    """

    Args:

        bbox_tuples (list): List of 4 corner tuples representing a bounding box.

    Returns:

        tuple: (SW_lat_lng, NE_lat_lng) as coordinate pairs.

    """

    lat_sw = bbox_tuples[0][1]

    lng_sw = bbox_tuples[0][0]

    lat_ne = bbox_tuples[2][1]

    lng_ne = bbox_tuples[2][0]

    return (lat_sw, lng_sw), (lat_ne, lng_ne)



"""

This is the main function of this module

Converts JSON data representing places into a KMZ file with KML content.

"""

def json_to_kmz(j_file, bbox_tuples, search_term):

    """

    Args:

        j_file (str or dict): JSON file path or data dictionary of places.

        bbox_tuples (list): List of coordinate tuples forming a bounding box.

        search_term (str): Term used for the location search.

    Returns:

        BytesIO: A KMZ (zipped KML) file object as a binary stream.

    """

    output = BytesIO()

    kml = simplekml.Kml()



    # Add bounding box polygon

    pol = kml.newpolygon(name='Search Area')

    pol.outerboundaryis = bbox_tuples

    pol.style.linestyle.color = simplekml.Color.red

    pol.style.linestyle.width = 2

    pol.style.polystyle.fill = 0

    sw, ne = get_nw_se_coordinates(bbox_tuples)

    pol.description = f'''

                        Search Term: {search_term}\n

                        SW coordinate: ({sw[0]}, {sw[1]})\nNE coordinate: ({ne[0]}, {ne[1]})

                       '''



    data = json_to_dict(j_file)

    locations = []



    for item in data['places']:

        name = get_string(item['name'], 'original_name') + ':' + get_string(item['name'], 'translated_name')

        loc_type = generalize(get_string(item, 'type'))

        website = get_string(item, 'website')

        phone = get_string(item, 'phone_number')

        addr = get_string(item, 'address')

        lat = get_string(item, 'latitude')

        lng = get_string(item, 'longitude')

        hours = format_hours(get_list(item, 'working_hours'))

        url = get_string(item, 'google_maps_url')



        #this was the only way to format the information on kmz

        desc = f"""

        Phone: {phone}



        Address: {addr}



        Website: {website}



        Hours: {hours}



        Google Maps: {url}

        """.strip()



        icon_url = get_icon(loc_type)

        locations.append({"name": name, "coords": (lng, lat), "desc": desc, 'icon': icon_url})



    for item in locations:

        pnt = kml.newpoint(name=item["name"], coords=[item["coords"]])

        pnt.description = item["desc"]

        pnt.style.iconstyle.icon.href = item["icon"]

        pnt.style.iconstyle.scale = 1.5



    output.write(kml.kml().encode('utf-8'))

    output.seek(0)

    return output

