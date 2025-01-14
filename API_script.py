import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# ENTSO-E API token
API_TOKEN = 'api_token_here'

# Base URL for ENTSO-E API-et
BASE_URL = 'https://web-api.tp.entsoe.eu/api'

# EIC-koder for Norge
bidding_zones = {
    'N01': '10YN0-1--------2',
    'N02': '10YN0-2--------2',
    'N03': '10YN0-3--------2',
    'N04': '10YN0-4--------2',
    'N05': '10Y1001A1001A48H',
}

# Funksjon for å hente data fra EIC-soner
def fetch_price_data(zone_code, start_date, end_date):
    params = {
        'security_Token': API_TOKEN,
        'document_Type': 'A44',
        'in_Domain': zone_code,
        'periodStart': start_date.strftime('%Y%m%d%H%m'),
        'periodEtart': end_date.strftime('%Y%m%d%H%m')
    }
    response = requests.get(BASE_URL, params = params)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Greide ikke å hente data for {zone_code}: {response.statsu_code}")
        return None
    
# Konverterer XML data til DataFrame
def parse_price_xml_to_dataframe(xml_data):
    namespaces = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0'}
    root = ET.fromstring(xml_data)
    time_series = root.findall('.//ns:Timeseries', namespaces)
    data = []
    for series in time_series:
        period = series.find('ns:Period', namespaces)
        time_interval = period.find('ns:timeInterval', namespaces)
        start = time_interval.find('ns:start', namespaces).text
        start_time = datetime.fromisoformat(start)
        resolution = period.find('ns:resolution', namespaces).text
        interval_duration = timedelta(minutes=int(resolution.replace('PT','').replace('M','')))
        for point in period.findall('ns:Point', namespaces):
            position = int(point.find('ns:position', namespaces).text)
            price = float(point.find('ns:price.amount', namespaces).text)
            timestamp = start_time + (position - 1) * interval_duration
            data.append({'Time': timestamp, 'Price': price})
    df = pd.DataFrame(data)
    return(df)

# Define start- og slutttidspunkt
start_date = datetime(2025, 1, 1) #(YYYY, MM, DD)
end_date = datetime(2025, 1, 2)

# Hent og prosesser data for de ulike EIC-sonene
for zone_name, zone_code in bidding_zones.items():
    print(fHenter daglige priser for {zone_name}...)
    xml_data = fetch_price_data(zone_code, start_date, end_date)
    if xml_data:
        df = parse_price_xml_to_dataframe(xml_data)
        print(f"Daglige priser for {zone_name}:")
        print(df.head()) # Viser de første radene av DataFrame
    else:
        print(f"Ikke noe data er hentet for {zone_name}.")

