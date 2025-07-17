import xlsxwriter
import json
import re
from io import BytesIO

# --- Helper Functions ---
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
    return business_hours_list or "unavailable"

def get_value(data, key, default="unavailable"):
    """Safely retrieves a value from a dictionary, handling nested keys if needed."""
    if not isinstance(data, dict):
        return default
    return data.get(key, default)

def get_cid(uri):
    """Extracts the Google CID from a Google Maps URL."""
    if not isinstance(uri, str):
        return 'Invalid URL'
    match = re.search(r'cid=(\d+)', uri)
    return match.group(1) if match else 'No cid number'

# --- Excel Sheet Creation and Formatting ---

def create_formats(workbook):
    """Creates and returns a dictionary of named cell formats for the workbook."""
    return {
        'header': workbook.add_format({
            'bold': True, 'font_size': 14, 'bg_color': '#C6EFCE', 'border': 1, 
            'align': 'center', 'valign': 'vcenter'
        }),
        'body': workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True
        }),
        'link': workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_color': 'blue', 'underline': 1
        }),
        'hours': workbook.add_format({
            'border': 1, 'align': 'left', 'valign': 'top', 'text_wrap': True
        })
    }

def setup_sheet(workbook, name, headers, widths, formats, default_row_height=100):
    """Creates a worksheet, writes the header, and applies formatting."""
    sheet = workbook.add_worksheet(name)
    sheet.write_row(0, 0, headers, formats['header'])
    sheet.freeze_panes(1, 0)
    for i, width in enumerate(widths):
        sheet.set_column(i, i, width)
    if default_row_height:
        sheet.set_default_row(default_row_height)
    return sheet

def create_detail_sheet(workbook, name, cid, addr, reviews, formats):
    """Creates a worksheet for individual location reviews."""
    sheet_name = f"{name[:15]}_{cid[:10]}"
    headers = ('CID', 'Name', 'Address', 'Orig. Author', 'Tran. Author', 'Orig. Text', 
               'Orig. Lang', 'Translated', 'Rating', 'Date', 'URL')
    widths = [20, 20, 30, 15, 15, 25, 10, 20, 10, 10, 40]
    sheet = setup_sheet(workbook, sheet_name, headers, widths, formats)
    
    if not isinstance(reviews, list):
        sheet.write(1, 0, "reviews unavailable", formats['body'])
        return sheet_name

    for row_num, review in enumerate(reviews, start=1):
        author = get_value(review, 'author_name', {})
        review_data = [
            cid, name, addr,
            get_value(author, 'original_name'), get_value(author, 'translated_name'),
            get_value(review, 'original_text'), get_value(review, 'original_language'),
            get_value(review, 'text'), get_value(review, 'rating'),
            get_value(review, 'publish_date')
        ]
        sheet.write_row(row_num, 0, review_data, formats['body'])
        sheet.write_url(row_num, 10, get_value(review, 'review_url', '#'), formats['link'])
    return sheet_name

def create_images_sheet(workbook, name, cid, addr, prompt, street, photos, formats):
    """Creates a worksheet for image information and insights."""
    sheet_name = f"{name[:13]}_images_{cid[:10]}"
    headers = ('CID', 'Name', 'Address', 'Tags', 'Summary', 'Link')
    widths = [20, 20, 30, 25, 40, 40]
    sheet = setup_sheet(workbook, sheet_name, headers, widths, formats)

    # --- Street View Data ---
    if isinstance(street, dict):
        street_info = [cid, name, addr, "street view", get_value(street, 'vlm_insight')]
        sheet.write_row(1, 0, street_info, formats['body'])
        
        # Check the URL before writing
        url = get_value(street, 'url', '#')
        if url.startswith('http'):
            sheet.write_url(1, 5, url, formats['link'])
        else:
            # Write as plain text
            sheet.write(1, 5, url, formats['body']) 
    else:
        sheet.write(1, 0, "street view unavailable", formats['body'])

    # --- Photos Data ---
    if isinstance(photos, list):
        for row_num, photo in enumerate(photos, start=2):
            photo_data = [
                cid, name, addr, prompt, 
                get_value(photo, 'vlm_insight')
            ]
            sheet.write_row(row_num, 0, photo_data, formats['body'])
        
            # Check the URL before writing
            url = get_value(photo, 'url', '#')
            if url.startswith('http'):
                sheet.write_url(row_num, 5, url, formats['link'])
            else:
                # Write as plain text
                sheet.write(row_num, 5, url, formats['body']) 
    else:
         sheet.write(2, 0, "photos unavailable", formats['body'])
         
    return sheet_name

# --- Main Function ---
def json_to_excel(j_file):
    """Converts a JSON object to a robust, multi-sheet Excel file in memory."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'strings_to_urls': False})
    formats = create_formats(workbook)
    data = json_to_dict(j_file)

    # Declarative mapping of headers to data extraction logic
    HEADER_CONFIG = {
        'Name (Orig.)':        (20, lambda loc: get_value(loc.get('name', {}), 'original_name')),
        'Name (Tran.)':        (20, lambda loc: get_value(loc.get('name', {}), 'translated_name')),
        'Address':             (30, lambda loc: get_value(loc, 'address')),
        'Phone':               (15, lambda loc: get_value(loc, 'phone_number')),
        'Latitude':            (12, lambda loc: get_value(loc, 'latitude')),
        'Longitude':           (12, lambda loc: get_value(loc, 'longitude')),
        'Hours':               (20, lambda loc: format_hours(get_value(loc, 'working_hours'))),
        'Website':             (30, lambda loc: get_value(loc, 'website')),
        'Google URL':          (40, lambda loc: get_value(loc, 'Maps_url')),
        'CID':                 (15, lambda loc: get_cid(get_value(loc, 'Maps_url'))),
        'Review Summary':      (25, lambda loc: get_value(loc, 'reviews_summary')),
        'Rating':              (10, lambda loc: get_value(loc, 'rating')),
        'Review Range':        (15, lambda loc: get_value(loc, 'reviews_span')),
        'Summary of Images':   (40, lambda loc: get_value(loc, 'photos_summary')),
        'Photos URL':          (40, lambda loc: get_value(loc, 'url_to_all_photos')),
        'Review Link':         (15, lambda loc: f"internal:'{loc.get('_review_sheet_name', '')}'!A1" if loc.get('_review_sheet_name') else 'N/A'),
        'Images Link':         (15, lambda loc: f"internal:'{loc.get('_image_sheet_name', '')}'!A1" if loc.get('_image_sheet_name') else 'N/A'),
    }

    main_headers = list(HEADER_CONFIG.keys())
    main_widths = [config[0] for config in HEADER_CONFIG.values()]
    main_sheet = setup_sheet(workbook, "Locations", main_headers, main_widths, formats)

    for row_num, location in enumerate(data.get('places', []), start=1):

        if 'reviews' in location:
            name = get_value(location.get('name', {}), 'translated_name')
            cid = get_cid(get_value(location, 'Maps_url'))
            addr = get_value(location, 'address')
            location['_review_sheet_name'] = create_detail_sheet(
                workbook, name, cid, addr, location['reviews'], formats
            )
        # Add similar logic for images if create_images_sheet is used
        if 'photos' in location:
            prompt = get_value(location, 'prompt_used')
            street_view = get_value(location, 'street_view')
            location['_image_sheet_name'] = create_images_sheet(
                workbook, name, cid, addr, prompt, street_view, location['photos'], formats
            )

        # Write data to the main sheet using the configuration map
        for col_num, header in enumerate(main_headers):
            value_extractor = HEADER_CONFIG[header][1]
            value = value_extractor(location)

            # Determine format and use the correct write method
            if str(value).startswith('http'):
                main_sheet.write_url(row_num, col_num, value, formats['link'], string='Link')
            elif str(value).startswith('internal:'):
                main_sheet.write_url(row_num, col_num, value, formats['link'], string='Details')
            elif header == 'Hours':
                main_sheet.write(row_num, col_num, value, formats['hours'])
            else:
                main_sheet.write(row_num, col_num, value, formats['body'])
                
    workbook.close()
    output.seek(0)
    return output