import xlsxwriter
import json
import copy
import io
import re

#TODO: some issues to consider-
# there are a number of rules assosciated with naming an excel sheet (special characters, length, etc...)
# a big one is they cant be duplicated
# I implemented a system that sanitizes, truncates, and increments them if needed (McDonalds, McDonalds2, etc.)
# But this made me realize that with up to 60 sheets in an excel, its gonna be REALLY hard for the user to correlate these increments to the og
# don't plan on fixing it now but its something we are going to have to deal with

# pin main tab to the bottom of workbook
# link to corresponding tab
# change tab name to: (place name + x digits of address) ex: 'Starbucks 1015'

def json_to_dict(j_file):
    if isinstance(j_file, str):
        with open(j_file, "r", encoding="utf-8") as file:
            dictionary = json.load(file)
    else:
        dictionary = copy.deepcopy(j_file)
    return dictionary

def format_hours(business_hours_list):
    return "\n".join(business_hours_list) if business_hours_list else "Hours unavailable"

def head_format():
    return {'bold': True, 'font_size': 14, 'bg_color': '#C6EFCE', 'border': 1, 'align': 'center', 'valign': 'vcenter'}

def bod_format():
    return {'border': 1, 'align': 'left', 'valign': 'vcenter'}

def links_format():
    return {'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_color': 'blue', 'underline': 1}

def hour_format():
    return {'border': 1, 'align': 'left', 'valign': 'top', 'text_wrap': True}

def get_string(data, val):
    return str(data.get(val, "unavailable"))

def get_list(data, val):
    return data.get(val, "unavailable")

def get_cid(data):
    if isinstance(data.get('reviews'), str):
        return get_string(data, 'name')[:31]  # Ensure the name is truncated to 31 characters
    try:
        position = data['reviews'][0].rfind(':')
        cid = data['reviews'][0][position+1:]
        return cid[:31]  # Ensure the cid is truncated to 31 characters
    except:
        return get_string(data, 'name')[:31]  # Truncate name if something goes wrong

# # this version uses cid as the worksheets title
# def json_to_excel(j_file):
#     mydict = json_to_dict(j_file)
#     output = io.BytesIO()  # Create an in-memory file
#     workbook = xlsxwriter.Workbook(output)
#     locationsheet = workbook.add_worksheet("Locations")
    
#     header = ('Name', 'Address', 'Phone', 'Latitude', 'Longitude', 'Hours', 'Rating', 'Website')
#     header_format = workbook.add_format(head_format())
#     locationsheet.write_row(0, 0, header, header_format)
    
#     body_format = workbook.add_format(bod_format())
#     hours_format = workbook.add_format(hour_format())
#     link_format = workbook.add_format(links_format())
    
#     data = []
#     for location in mydict['places']:
#         name = get_string(location, 'name')
#         website = get_string(location, 'website')
#         phone = get_string(location, 'phone_number')
#         addr = get_string(location, 'address')
#         lat = get_string(location, 'latitude')
#         lng = get_string(location, 'longitude')
#         rating = get_string(location, 'rating')
#         hours = format_hours(get_list(location, 'working_hours'))
#         data.append((name, addr, phone, lat, lng, hours, rating, website))
        
#         cid = get_cid(location)
#         temp = workbook.add_worksheet(cid)
#         temp.write(0, 0, "Picture Links", header_format)
#         photos = get_list(location, 'photos')
#         if isinstance(photos, str):
#             temp.write(1, 0, photos)
#         else:
#             for row_num, link in enumerate(photos):
#                 temp.write(row_num+1, 0, link, link_format)
    
#     for row_num, row_data in enumerate(data, start=1):
#         for col_num, value in enumerate(row_data):
#             format_to_use = hours_format if col_num == 6 else body_format
#             locationsheet.write(row_num, col_num, value, format_to_use)
    
#     max_column_width = 90
#     for col_num, col_name in enumerate(header):
#         max_length = max(len(str(row[col_num])) for row in data) if data else len(col_name)
#         col_width = min(max_length + 2, max_column_width)
#         locationsheet.set_column(col_num, col_num, col_width)
    
#     workbook.close()
#     output.seek(0)  # Reset file pointer to start
#     return output

# this version uses place name as the worksheets title
# Function to sanitize sheet names by replacing invalid characters
def sanitize_sheet_name(sheet_name):
    # List of invalid characters for Excel sheet names
    invalid_chars = r'[\\/\[\]\*\?:]'
    
    # Replace invalid characters with an underscore
    sheet_name = re.sub(invalid_chars, '_', sheet_name)
    
    # Remove leading or trailing apostrophes if any
    sheet_name = sheet_name.strip("'")
    
    # Ensure the name doesn't exceed 31 characters
    return sheet_name[:31]

def json_to_excel(j_file):
    mydict = json_to_dict(j_file)
    output = io.BytesIO()  # Create an in-memory file
    workbook = xlsxwriter.Workbook(output)
    locationsheet = workbook.add_worksheet("Locations")
    
    header = ('Name', 'Address', 'Phone', 'Latitude', 'Longitude', 'Hours', 'Rating', 'Website')
    header_format = workbook.add_format(head_format())
    locationsheet.write_row(0, 0, header, header_format)
    
    body_format = workbook.add_format(bod_format())
    hours_format = workbook.add_format(hour_format())
    link_format = workbook.add_format(links_format())
    
    data = []
    sheet_names_used = set()  # Set to keep track of sheet names already used
    for location in mydict['places']:
        name = get_string(location, 'name')
        website = get_string(location, 'website')
        phone = get_string(location, 'phone_number')
        addr = get_string(location, 'address')
        lat = get_string(location, 'latitude')
        lng = get_string(location, 'longitude')
        rating = get_string(location, 'rating')
        hours = format_hours(get_list(location, 'working_hours'))
        data.append((name, addr, phone, lat, lng, hours, rating, website))
        
        # Truncate name to 31 characters and sanitize it
        base_sheet_name = sanitize_sheet_name(name[:31])  # Truncate first, then sanitize
        
        # Handle duplicate sheet names by appending a number
        sheet_name = base_sheet_name
        increment = 2
        while sheet_name in sheet_names_used:
            sheet_name = f"_{base_sheet_name} {increment}"  # Prepend an underscore for safety
            # Ensure sheet name doesn't exceed 31 characters
            if len(sheet_name) > 31:
                sheet_name = f"_{base_sheet_name[:28]} {increment}"  # Adjust length if necessary
            increment += 1
        
        sheet_names_used.add(sheet_name)  # Add the new sheet name to the set
        temp = workbook.add_worksheet(sheet_name)
        temp.write(0, 0, "Picture Links", header_format)
        photos = get_list(location, 'photos')
        if isinstance(photos, str):
            temp.write(1, 0, photos)
        else:
            for row_num, link in enumerate(photos):
                temp.write(row_num+1, 0, link, link_format)
    
    for row_num, row_data in enumerate(data, start=1):
        for col_num, value in enumerate(row_data):
            format_to_use = hours_format if col_num == 6 else body_format
            locationsheet.write(row_num, col_num, value, format_to_use)
    
    max_column_width = 90
    for col_num, col_name in enumerate(header):
        max_length = max(len(str(row[col_num])) for row in data) if data else len(col_name)
        col_width = min(max_length + 2, max_column_width)
        locationsheet.set_column(col_num, col_num, col_width)
    
    workbook.close()
    output.seek(0)  # Reset file pointer to start
    return output




