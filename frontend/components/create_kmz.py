import simplekml

import zipfile

import json

import copy

from io import BytesIO



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


def get_nw_se_coordinates(bbox_tuples):
    lat_sw = bbox_tuples[0][1]
    lng_sw = bbox_tuples[0][0]
    lat_ne = bbox_tuples[2][1]
    lng_ne = bbox_tuples[2][0]

    return (lat_sw, lng_sw), (lat_ne, lng_ne)


def json_to_kmz(j_file, bbox_tuples, search_term):

    output = BytesIO()

    kml = simplekml.Kml()

    # adds the validated bounding box to the kmz
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





    

    

    output = BytesIO()

    output.write(kml.kml().encode('utf-8'))

    output.seek(0)

    

    #kml.save(outfile)

    #with zipfile.ZipFile(outfile, "w", zipfile.ZIP_DEFLATED) as kmz:

    #    kmz.write("link.kml")

    return output