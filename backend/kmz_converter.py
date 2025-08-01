import simplekml
import json
from io import BytesIO

# --- Constants ---
ICON_URLS = {
    "restaurant": "http://maps.google.com/mapfiles/kml/shapes/dining.png",
    "hotel": "http://maps.google.com/mapfiles/kml/shapes/lodging.png",
    "shopping": "http://maps.google.com/mapfiles/kml/shapes/shopping.png",
    "park": "http://maps.google.com/mapfiles/kml/shapes/parks.png",
    "default": "http://maps.google.com/mapfiles/kml/shapes/info-i.png"
}
TYPE_MAPPING = {
    "restaurant": "restaurant", "food": "restaurant", "eat": "restaurant", 
    "cuisine": "restaurant", "cafe": "restaurant",
    "hotel": "hotel", "motel": "hotel", "resort": "hotel", 
    "inn": "hotel", "lodge": "hotel", "cabin": "hotel",
    "store": "shopping", "deli": "shopping", "bakery": "shopping", 
    "grocery": "shopping", "market": "shopping",
    "park": "park"
}

# --- Functions ---
def json_to_dict(j_file):
    """Converts a JSON file path or dictionary object into a dictionary."""
    if isinstance(j_file, str):
        with open(j_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return j_file if isinstance(j_file, dict) else {}

def format_hours(business_hours_list):
    """Formats a list of business hours into a newline-separated string."""
    if isinstance(business_hours_list, list):
        return "\n".join(business_hours_list)
    return business_hours_list if business_hours_list else "unavailable"

def get_string(data, val):
    """Gets a value from a dict as a string, returning 'unavailable' if not found."""
    return str(data.get(val, "unavailable"))

def get_list(data, val):
    """Gets a list from a dict, returning 'unavailable' if not found."""
    return data.get(val, "unavailable") if isinstance(data, dict) else "unavailable"

def get_icon(loc_type):
    """Gets the icon URL for a given location type."""
    return ICON_URLS.get(loc_type.lower(), ICON_URLS["default"])

def generalize(name):
    """Generalizes a specific location type using a direct mapping."""
    return TYPE_MAPPING.get(str(name).lower(), "default")

def get_sw_ne_coordinates(bbox_tuples):
    """Extracts SW and NE coordinates from bounding box tuples."""
    sw_lng, sw_lat = bbox_tuples[0]
    ne_lng, ne_lat = bbox_tuples[2]
    return (sw_lat, sw_lng), (ne_lat, ne_lng)

def json_to_kmz(j_file, bbox_tuples, search_term):
    """
    Creates a KMZ file in memory from JSON data of places.

    Args:
        j_file (str or dict): JSON file path or data dictionary.
        bbox_tuples (list): List of coordinate tuples for the bounding box.
        search_term (str): The search term used.

    Returns:
        BytesIO: A KMZ file object as a binary stream.
    """
    output = BytesIO()
    kml = simplekml.Kml()
    data = json_to_dict(j_file)

    # Add bounding box polygon
    pol = kml.newpolygon(name='Search Area')
    pol.outerboundaryis = bbox_tuples
    pol.style.linestyle.color = simplekml.Color.red
    pol.style.linestyle.width = 2
    pol.style.polystyle.fill = 0
    sw, ne = get_sw_ne_coordinates(bbox_tuples)
    pol.description = f"Search Term: {search_term}\nSW: {sw}\nNE: {ne}"

    # Process each place and add it directly to the KML object
    for item in data.get('places', []):
        name_data = item.get('name', {})
        name = f"{get_string(name_data, 'original_name')}:{get_string(name_data, 'translated_name')}"
        
        desc = f"""
        Phone: {get_string(item, 'phone_number')}
        Address: {get_string(item, 'address')}
        Website: {get_string(item, 'website')}
        Hours: {format_hours(get_list(item, 'working_hours'))}
        Google Maps: {get_string(item, 'Maps_url')}
        """.strip()

        coords = (get_string(item, 'longitude'), get_string(item, 'latitude'))
        loc_type = generalize(get_string(item, 'type'))
        
        pnt = kml.newpoint(name=name, coords=[coords])
        pnt.description = desc
        pnt.style.iconstyle.icon.href = get_icon(loc_type)
        pnt.style.iconstyle.scale = 1.5

    kml.savekmz(output)
    output.seek(0)
    return output