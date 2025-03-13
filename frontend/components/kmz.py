import simplekml
import zipfile
import json
import copy

def json_to_dict(j_file):
    if isinstance(j_file, str):
        with open(j_file, "r", encoding="utf-8") as file:
            dictionary = json.load(file)
    else:
        dictionary = copy.deepcopy(j_file)
    return dictionary

def format_hours(business_hours_list):
    return "\n".join(business_hours_list) if isinstance(business_hours_list, list) else business_hours_list

def get_string(data, val):
    try:
        answer = data[val]
        return str(answer)
    except:
        return "unavailable"

def get_list(data, val):
    return data.get(val, "unavailable") if isinstance(data, dict) else "unavailable"

def get_icon(type):
    """Return an icon URL based on the location type."""
    icons = {
        "restaurant": "http://maps.google.com/mapfiles/kml/shapes/dining.png",
        "hotel": "http://maps.google.com/mapfiles/kml/shapes/lodging.png",
        "shopping": "http://maps.google.com/mapfiles/kml/shapes/shopping.png",
        "park": "http://maps.google.com/mapfiles/kml/shapes/parks.png",
        "default": "http://maps.google.com/mapfiles/kml/shapes/info-i.png"
    }
    return icons.get(type.lower(), icons["default"])

def generalize(name):
    types = {"restaurant": ("restaurant", "food", "eat", "cuisine", "cafe"),
             "hotel": ("hotel", "motel", "resort", "inn", "lodge", "cabin"),
             "shopping": ("store", "deli", "bakery", "grocery", "market"),
             "park": ("park")}
    for key, item in types.items():
        if name in item:
            return key
    return "default"
    

def json_to_kmz(j_file, outfile="locations.kmz"):
    kml = simplekml.Kml()
    
    data = json_to_dict(j_file)
    
    locations = []
    for item in data['places']:
        name = get_string(item, 'name')
        loc_type = generalize(get_string(item, 'type'))
        website = get_string(item, 'website')
        phone = get_string(item, 'phone_number')
        addr = get_string(item, 'address')
        lat = get_string(item, 'latitude')
        lng = get_string(item, 'longitude')
        hours = format_hours(get_list(item, 'working_hours'))
        url = get_string(item, 'google_maps_url')
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
        pnt.style.iconstyle.icon.href = item["icon"]  # Set custom icon
        pnt.style.iconstyle.scale = 1.5


    kml.save("link.kml")


    with zipfile.ZipFile(outfile, "w", zipfile.ZIP_DEFLATED) as kmz:
        kmz.write("link.kml")