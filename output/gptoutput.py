import xlsxwriter
import json

def json_to_dict(j_file_path):
    with open(j_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def format_business_hours(business_hours_list):
    """Formats business hours so each day appears on a new line."""
    formatted_hours = "\n".join(business_hours_list) if business_hours_list else "Hours unavailable"
    return formatted_hours

def write_to_excel(header, data):
    workbook = xlsxwriter.Workbook("example.xlsx")
    worksheet = workbook.add_worksheet()

    # Define header format
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'bg_color': '#C6EFCE',  # Light green background
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })

    # Define body format
    body_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })

    # Define format for the "Hours" column (text wrapping enabled)
    hours_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'top',
        'text_wrap': True  # Ensures multi-line display
    })

    # Write the header row with formatting
    worksheet.write_row(0, 0, header, header_format)

    # Write the data rows with body formatting
    for row_num, row_data in enumerate(data):
        for col_num, cell_data in enumerate(row_data):
            # Apply special format for the "Hours" column
            if col_num == 5:  # Index 5 corresponds to "Hours"
                worksheet.write(row_num + 1, col_num, cell_data, hours_format)
            else:
                worksheet.write(row_num + 1, col_num, cell_data, body_format)

    # Auto-adjust column width but limit to max 1/8 of page width (approx. 90 chars)
    max_column_width = 90
    for col_num, col_name in enumerate(header):
        max_length = max(len(str(row[col_num])) for row in data) if data else len(col_name)
        col_width = min(max_length + 2, max_column_width)
        worksheet.set_column(col_num, col_num, col_width)

    # Close the workbook to save the file
    workbook.close()

def json_to_excel(j_file_path):
    header = ('Name', 'Address', 'Phone', 'Latitude', 'Longitude', 'Hours', 'Website', 'Location Link', 'CID')
    data = []
    mydict = json_to_dict(j_file_path)

    for location in mydict['places']:
        name = location.get('displayName', {}).get('text', "Name unavailable")
        addr = location.get('formattedAddress', "Address unavailable")
        phone = location.get('nationalPhoneNumber', "Phone number unavailable")
        lat = location.get('location', {}).get('latitude', "Location unavailable")
        long = location.get('location', {}).get('longitude', "Location unavailable")
        hours = format_business_hours(location.get('regularOpeningHours', {}).get('weekdayDescriptions', []))
        website = location.get('websiteUri', "Website unavailable")
        g_link = location.get('googleMapsUri', "Google Maps link unavailable")
        cid = g_link.split("cid=")[1] if "cid=" in g_link else "CID unavailable"

        data.append((name, addr, phone, lat, long, hours, website, g_link, cid))

    write_to_excel(header, data)

