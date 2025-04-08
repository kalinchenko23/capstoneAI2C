"""
This module is to get json file/raw data then extracts it to excel
There are 10 total functions:

json_to_dict(j_file) - converts file into json 
format_hours(business_hours_list) - formats hours information to a location
create_formats(workbook) - formats for header, body, links, hours
adjust_column_widths(sheet, widths) - adjusts to width of cell
adjust_row_heights(sheet, max_height=100) - adjusts the height of cell
get_string(data, val) - gets string data from json
get_list(data, val) - gets list data from json
get_cid(uri) - gets CID information from google maps url
create_main_sheet(workbook, formats) - creates main sheet & formats
create_detail_sheet(workbook, name, cid, addr, reviews, formats) - creates separate review sheet 
create_images_sheet(workbook, name, cid, addr, prompt, street, photos, formats) - creates image sheet
json_to_excel(j_file) - main function 
"""
import xlsxwriter
import json
import copy
import re
from io import BytesIO

"""
Purpose of this function is to take j_file & turn it to dictionary
If the j_file is a path to json text, it converts to json dictionary
If the j_file is a raw jason, copy it then return the copy
"""
def json_to_dict(j_file):
    """
    Args:
        j_file (str/json): Path to a JSON file or raw json.
    Returns:
        dict: Parsed JSON dictionary.
    """
    if isinstance(j_file, str): #if j_file is string, it must be a file
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
        business_hours_list (list or str): Business hours.
    Returns:
        str: Newline-separated hours or the original string.
    """
    if isinstance(business_hours_list, list):
        return "\n".join(business_hours_list)  
    else: 
        return business_hours_list

"""
Creates cell formats for the Excel workbook.
Title - green background, bigger font, bold
Body - text wrap
link - blue & underlined
hours - top first
"""
def create_formats(workbook):
    """
    Args:
        workbook (xlsxwriter.Workbook): The workbook object.
    Returns:
        dict: Dictionary of named cell formats.
    """
    return {
        'header': workbook.add_format({
            'bold': True, 'font_size': 14, 'bg_color': '#C6EFCE', 'border': 1, 'align': 'center', 'valign': 'vcenter'
        }),
        'body': workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True}),
        'link': workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_color': 'blue', 'underline': 1}),
        'hours': workbook.add_format({'border': 1, 'align': 'left', 'valign': 'top', 'text_wrap': True})
    }

"""
Sets column widths in a worksheet.
"""
def adjust_column_widths(sheet, widths):
    """
    Args:
        sheet (xlsxwriter.Worksheet): Worksheet to modify.
        widths (list): List of column widths.
    """
    for i, width in enumerate(widths):
        sheet.set_column(i, i, width)

"""
Sets row height for rows in the worksheet.
100 is max & default
"""
def adjust_row_heights(sheet, max_height=100):
    """
    Args:
        sheet (xlsxwriter.Worksheet): Worksheet to modify.
        max_height (int, optional): Height for each row. Defaults to 100.
    """
    for row in range(1, 1000):
        sheet.set_row(row, max_height)

"""
Safely retrieves a string value from a dictionary.
if its str - should return "not available"
if something goes wrong in dictionary returns "unavailable"
returns value of whatever key in string
"""
def get_string(data, val):
    """
    Args:
        data (dict): Data dictionary.
        val (str): Key to extract.
    Returns:
        str: String value or 'unavailable'.
    """
    if isinstance(data, dict):
        return str(data.get(val, "unavailable"))  
    else:
        return str(data)

"""
Safely retrieves a list from a dictionary.
If the list is empty is will return 'unavailable'
If the something goes wrong in dictionary, returns 'unavailable'
returns values of whatver key in list
"""
def get_list(data, val):
    """
    Args:
        data (dict): Data dictionary.
        val (str): Key to extract.
    Returns:
        list or str: Value list or 'unavailable'.
    """
    if isinstance(data, dict):
        return data.get(val, "unavailable")  
    else: 
        return "unavailable"

"""
CID is custome idenfication from google, this IDs locations
It extracts the CID digits from the url 
If no number found, it returns 'No cid number'
"""
def get_cid(uri):
    """
    Args:
        uri (str): Google Maps URL.
    Returns:
        str: CID or 'No cid number'.
    """
    cid = re.search(r'cid=(\d+)', uri)
    return cid.group(1) if cid else 'No cid number'

"""
Creates the main 'Locations' sheet in the Excel file.
It creates sheet called - Locations
Writes the headers (title)
Formats row, freezes the title for scrolling & Formats 
"""
def create_main_sheet(workbook, formats, option):
    """
    Args:
        workbook (xlsxwriter.Workbook): The workbook object.
        formats (dict): Dictionary of Excel cell formats.
    Returns:
        xlsxwriter.Worksheet: Created worksheet.
    """
    sheet = workbook.add_worksheet("Locations")
    header = ('Name (Orig.)', 'Name (Tran.)', 'Address', 'Phone', 'Latitude', 'Longitude', 'Hours',
              'Website', 'Google URL', 'CID')
    column_widths = (20, 20, 30, 15, 12, 12, 20, 30, 40, 15)
    
    if option[0]:
        header += ('Review Summary', 'Rating', 'Review Range')
        column_widths += (25, 10, 15)
    if option[1]:
        header += ('Summary of Image', 'Photos URL')
        column_widths += (40, 40)
    if option[0]:
        header += ('Review Link',)
        column_widths += (40,)
    if option[1]:
        header += ('Images Link',)
        column_widths += (40,)
    
    sheet.write_row(0, 0, header, formats['header'])
    sheet.freeze_panes(1, 0)
    
    
    adjust_column_widths(sheet, column_widths)
    adjust_row_heights(sheet)
    return sheet

"""
Creates a worksheet for individual location reviews & information
Then formats the new sheet, then writes the review information
"""
def create_detail_sheet(workbook, name, cid, addr, reviews, formats):
    """
    Args:
        workbook (xlsxwriter.Workbook): Workbook object.
        name (str): Location name.
        cid (str): Google CID.
        addr (str): Address.
        reviews (list or str): Review data.
        formats (dict): Format styles.
    Returns:
        str: Name of the created worksheet.
    """
    sheet_name = (name[:15] if len(name) > 15 else name) + '_' + cid[:10]
    sheet = workbook.add_worksheet(sheet_name)
    header = ('CID', 'Name', 'Address', 'Orig. Author', 'Tran. Author', 'Orig. Text', 'Orig. Lang', 'Translated',
              'Rating', 'Date', 'URL')
    sheet.write_row(0, 0, header, formats['header'])
    sheet.freeze_panes(1, 0)
    column_widths = [20, 20, 30, 15, 15, 25, 10, 20, 10, 10, 145]
    adjust_column_widths(sheet, column_widths)
    adjust_row_heights(sheet)

    if isinstance(reviews, str):
        sheet.write(1, 0, reviews, formats['body'])
    else:
        for row_num, review in enumerate(reviews, start=1):
            sheet.write(row_num, 0, cid, formats['body'])
            sheet.write(row_num, 1, name, formats['body'])
            sheet.write(row_num, 2, addr, formats['body'])
            sheet.write(row_num, 3, get_string(review['author_name'], 'original_name'), formats['body'])
            sheet.write(row_num, 4, get_string(review['author_name'], 'translated_name'), formats['body'])
            sheet.write(row_num, 5, get_string(review, 'original_text'), formats['body'])
            sheet.write(row_num, 6, get_string(review, 'original_language'), formats['body'])
            sheet.write(row_num, 7, get_string(review, 'text'), formats['body'])
            sheet.write(row_num, 8, get_string(review, 'rating'), formats['body'])
            sheet.write(row_num, 9, get_string(review, 'publish_date'), formats['body'])
            sheet.write(row_num, 10, get_string(review, 'review_url'), formats['link'])

    return sheet_name


"""
Creates a worksheet for image information
Then formats the new sheet, then writes the review information
First row is the street view image information
The following rows are the pictures information found on google 
"""
def create_images_sheet(workbook, name, cid, addr, prompt, street, photos, formats):
    """
    Args:
        workbook (xlsxwriter.Workbook): Workbook object.
        name (str): Location name.
        cid (str): Google CID.
        addr (str): Address.
        prompt (str): Prompt used to generate insights.
        street (dict or str): Street view data.
        photos (list or str): Photos data.
        formats (dict): Format styles.

    Returns:
        str: Name of the created worksheet.
    """
    sheet_name = (name[:13] if len(name) > 13 else name) + '_images_' + cid[:10]
    sheet = workbook.add_worksheet(sheet_name)
    header = ('CID', 'Name', 'Address', 'Tags', 'Summary', 'Link')
    sheet.write_row(0, 0, header, formats['header'])
    sheet.freeze_panes(1, 0)
    column_widths = [20, 20, 30, 25, 25, 145]
    adjust_column_widths(sheet, column_widths)
    adjust_row_heights(sheet)

    if isinstance(street, str):
        sheet.write(1, 0, street, formats['body'])
    else:
        street_info = (cid, name, addr, "street view", street['vlm_insight'])
        sheet.write_row(1, 0, street_info, formats['body'])
        url = street['url']
        sheet.write(1, 5, url, formats['body'] if isinstance(url, str) else formats['link'])

    if isinstance(photos, str):
        sheet.write(2, 0, photos, formats['body'])
    else:
        for row_num, photos in enumerate(photos, start=1):
            sheet.write(row_num + 1, 0, cid, formats['body'])
            sheet.write(row_num + 1, 1, name, formats['body'])
            sheet.write(row_num + 1, 2, addr, formats['body'])
            sheet.write(row_num + 1, 3, prompt, formats['body'])
            sheet.write(row_num + 1, 4, get_string(photos, 'vlm_insight'), formats['body'])
            sheet.write(row_num + 1, 5, get_string(photos, 'url'), formats['link'])
    return sheet_name

"""
This is the main function of the output and integrates all functions above 
Converts a JSON object to an Excel file with formatted data.
"""
def json_to_excel(j_file):
    """
    Args:
        j_file (str or dict): JSON file path or dictionary object.
    Returns:
        BytesIO: In-memory Excel file stream.
    """
    mydict = json_to_dict(j_file) #converts j_file into json as necessary
    
    #To save the file in the memory
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    #creates formats for title, body, link, hours
    formats = create_formats(workbook)
    
    
    review = True if 'reviews' in mydict['places'][0] else False    
    photo = True if 'photos' in mydict['places'][0] else False
    
    option = (review, photo)

    #creates and sets up the main sheet 
    locations_sheet = create_main_sheet(workbook, formats, option)

    #extracts information 
    #creates review & image sheets as necessary
    #writes the informatin to the main sheet on excel
    #then outputs to a memeory/file
    for row_num, location in enumerate(mydict['places'], start=1):
        tra_name = get_string(location['name'], 'translated_name')
        ori_name = get_string(location['name'], 'original_name')
        cid = get_cid(get_string(location, 'google_maps_url'))
        addr = get_string(location, 'address')
        prompt = get_string(location, 'prompt_used')
        street_view = get_string(location, 'street_view')
        if 'reviews' in location:
            worksheet_review_name = create_detail_sheet(workbook, tra_name, cid, addr, location.get('reviews', []), formats)
            worksheet_review_link = f"internal:'{worksheet_review_name}'!A1"
        else:
            worksheet_review_link = 'unavailable'
        if 'photos' in location:
            worksheet_images_name = create_images_sheet(workbook, tra_name, cid, addr, prompt, street_view, location.get('photos', []), formats)
            worksheet_images_link = f"internal:'{worksheet_images_name}'!A1"
        else:
            worksheet_images_link = 'unavailable'
        data_tuple = (
            ori_name, tra_name, addr, get_string(location, 'phone_number'),
            get_string(location, 'latitude'), get_string(location, 'longitude'),
            format_hours(get_list(location, 'working_hours')),
            get_string(location, 'website'), get_string(location, 'google_maps_url'), cid)
            
        if option[0]:
            data_tuple += (get_string(location, 'reviews_summary'), get_string(location, 'rating'),
            get_string(location, 'reviews_span'))
            
        if option[1]:
            data_tuple += (get_string(location, 'photos_summary'), get_string(location, 'url_to_all_photos'))
            
        if option[0]:
            data_tuple += (worksheet_review_link,) 
            
        if option[1]:
            data_tuple += (worksheet_images_link,)

        for col_num, value in enumerate(data_tuple):
            if isinstance(value, list):
                value = "\n".join(map(str, value))
            format_to_use = formats['link'] if value.startswith("http") or value.endswith('!A1') else formats['body']
            locations_sheet.write(row_num, col_num, value, format_to_use)

    workbook.close()
    output.seek(0)

    #uncomment this if you want to save it as a file
    """
    with open("sample.xlsx", "wb") as f:
        f.write(output.read())
        output.seek(0)
    """
    return output
