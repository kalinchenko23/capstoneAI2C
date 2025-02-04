#from reportlab.pdfgen import canvas

import xlsxwriter
import json

def json_to_dict(j_file_path):
    with open(j_file_path, "r", encoding="utf-8") as file:
       data = json.load(file)
    return data

def format_business_hours(business_hours_list):
    formatted_hours = []
    for hours in business_hours_list:
        clean_hours = hours.replace("\u202f", " ").replace("\u2009", " ")
        formatted_hours.append(clean_hours)
        formatted_hours.append("\n")
    return "\n".join(formatted_hours)
    
def write_to_excel(header, data):
    workbook = xlsxwriter.Workbook("example.xlsx")
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, header)
    for row_num, row_data in enumerate(data):
        worksheet.write_row(row_num + 1, 0, row_data)
    workbook.close()


def json_to_excel(j_file_path):
    header = ('Name', 'Address', 'Phone', 'Latitue', 'Longitude', 'Hours', 'Website', 'Location Link', 'CID')
    data = []
    mydict = json_to_dict(j_file_path)
    for location in mydict['places']:
        if 'displayName' in location:
            name = location['displayName']['text']
        else:
            name = "name unavailable"
        if 'formattedAddress' in location:
            addr = location['formattedAddress']
        else:
            addr = "address unavailable"
        if 'nationalPhoneNumber' in location:
            phone = location['nationalPhoneNumber']
        else:
            phone = "phone number unavailable"
        if 'location' in location:
            lat = location['location']['latitude']
            long = location['location']['longitude']
        else:
            lat, long = "location unavailable"
        if 'regularOpeningHours' in location:
            hours = format_business_hours(location['regularOpeningHours']['weekdayDescriptions'])
        else:
            hours = "hours unavailable"
        if 'websiteUri' in location:
            locat = location["websiteUri"]
        else:
            locat = "website unavailable"
            
        if 'googleMapsUri' in location:
            g_link = location["googleMapsUri"]
            index = location["googleMapsUri"].find("cid=")
            cid = location["googleMapsUri"][index+4:]
        data.append((name, addr, phone, lat, long, hours, locat, cid)) 
    write_to_excel(header, data)
