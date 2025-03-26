import xlsxwriter

import json

import copy

import re

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



def create_formats(workbook):

    return {

        'header': workbook.add_format({

            'bold': True, 'font_size': 14, 'bg_color': '#C6EFCE', 'border': 1, 'align': 'center', 'valign': 'vcenter'

        }),

        'body': workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter', 'text_wrap': True}),

        'link': workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter', 'font_color': 'blue', 'underline': 1}),

        'hours': workbook.add_format({'border': 1, 'align': 'left', 'valign': 'top', 'text_wrap': True})

    }



def adjust_column_widths(sheet, widths):

    for i, width in enumerate(widths):

        sheet.set_column(i, i, width)



def adjust_row_heights(sheet, max_height=100):

    for row in range(1, 1000):  # Assuming a large enough row count

        sheet.set_row(row, max_height)



def get_string(data, val):

    return str(data.get(val, "unavailable")) if isinstance(data, dict) else str(data)



def get_list(data, val):

    return data.get(val, "unavailable") if isinstance(data, dict) else "unavailable"



def get_review_list(data):

    reviews = data.get('reviews', []) if isinstance(data, dict) else data

    if isinstance(reviews, str):

        return reviews

    if not isinstance(reviews, list):

        return 'Reviews data is not in the expected format'

    return "\n".join([item.get("review_url", "No URL") for item in reviews if isinstance(item, dict)]) or 'Reviews are not provided'



def get_vlm_summary(data):

    photos = data.get('photos', []) if isinstance(data, dict) else data

    if isinstance(photos, str):

        return photos

    return "\n".join([item.get("vlm_insight", "No Insight") for item in photos]) or 'Photos are not provided'



def get_cid(uri):

    cid = re.search(r'cid=(\d+)', uri)

    return cid.group(1) if cid else 'No cid number'



def create_main_sheet(workbook, formats):

    sheet = workbook.add_worksheet("Locations")

    header = ('Name (Orig.)', 'Name (Tran.)', 'Address', 'Phone', 'Latitude', 'Longitude', 'Hours',

              'Website', 'Google URL', 'CID', 'Review Summary', 'Rating',

              'Review Range', 'Summary of Image', 'Photos URL', 'Review Link', 'Images Link')

    sheet.write_row(0, 0, header, formats['header'])

    sheet.freeze_panes(1, 0)

    column_widths = [20, 20, 30, 15, 12, 12, 20, 30, 40, 15, 25, 10, 15, 40, 40, 40, 40]

    adjust_column_widths(sheet, column_widths)

    adjust_row_heights(sheet)

    return sheet



def create_detail_sheet(workbook, name, cid, addr, reviews, formats):

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



def create_images_sheet(workbook, name, cid, addr, prompt, street, photos, formats):

    sheet_name = (name[:13] if len(name) > 13 else name) + '_images_' + cid[:10]

    sheet = workbook.add_worksheet(sheet_name)

    header = ('CID', 'Name', 'Address', 'Tags', 'Summary', 'Link')

    sheet.write_row(0, 0, header, formats['header'])

    sheet.freeze_panes(1, 0)

    column_widths= [20, 20, 30, 25, 25, 145]

    adjust_column_widths(sheet, column_widths)

    adjust_row_heights(sheet)



    if isinstance(street, str): 

        sheet.write(1, 0, street, formats['body'])

    else:

        street_info = (cid, name, addr, "street view", street['vlm_insight'])

        sheet.write_row(1, 0, street_info, formats['body'])

        url = street['url']

        sheet.write(1,5, url, formats['body'] if isinstance(url, str) else formats['link'])



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



def json_to_excel(j_file):

    mydict = json_to_dict(j_file)

    

     # Create in-memory output

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output, {'in_memory': True})



    formats = create_formats(workbook)

    locations_sheet = create_main_sheet(workbook, formats)

    

    for row_num, location in enumerate(mydict['places'], start=1):

        tra_name = get_string(location['name'], 'translated_name')

        ori_name = get_string(location['name'], 'original_name')

        cid = get_cid(get_string(location, 'google_maps_url'))

        addr = get_string(location, 'address')

        prompt = get_string(location, 'prompt_used')

        street_view = location['street_view'] 

        worksheet_review_name = create_detail_sheet(workbook, tra_name, cid, addr, location.get('reviews', []), formats)

        worksheet_images_name = create_images_sheet(workbook, tra_name, cid, addr, prompt, street_view, location.get('photos', []), formats)

        worksheet_review_link = f"internal:'{worksheet_review_name}'!A1"

        worksheet_images_link = f"internal:'{worksheet_images_name}'!A1" 

        

        data_tuple = (

            ori_name,

            tra_name,

            addr, 

            get_string(location, 'phone_number'),

            get_string(location, 'latitude'), 

            get_string(location, 'longitude'),

            format_hours(get_list(location, 'working_hours')),

            get_string(location, 'website'), 

            get_string(location, 'google_maps_url'),

            cid,

            get_string(location, 'reviews_summary'),

            get_string(location, 'rating'),

            get_string(location, 'reviews_span'),

            get_string(location, 'photos_summary'),

            get_string(location, 'url_to_all_photos'),

            worksheet_review_link,

            worksheet_images_link

        )

        

        for col_num, value in enumerate(data_tuple):

            if isinstance(value, list):

                value = "\n".join(map(str, value))

            format_to_use = formats['link'] if col_num == 15 or col_num == 16 or (isinstance(value, str) and value.startswith("http")) else formats['body']

            locations_sheet.write(row_num, col_num, value, format_to_use)

    

    workbook.close()

    output.seek(0)

    

    # with open("sample.xlsx", "wb") as f:

    #     f.write(output.read())

    #     output.seek(0)

    

    return output

