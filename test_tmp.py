import requests
from datetime import datetime, timezone, tzinfo
import pytz
from influxdb_client.client import write_api
from pandas import DataFrame

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'influxdb-client'])
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS

# ToDo auf IfluxDB vom Büro anpassen
# INFLUXDB_URL = '172.30.33.3:8086'
INFLUXDB_URL = "http://localhost:8086"
# INFLUXDB_TOKEN = 'TOKEN'
INFLUXDB_TOKEN = '1R4LfbMgsv9wb6zl7NOosmiYnDJuZRsaXS8yrK6zrDDFdge6lENrXnTpD60kQ8HhY3-FsO2WMJ89Y6xjLxaAEg=='
INFLUXDB_ORG = 'homeassist'
INFLUXDB_BUCKET = 'homeassist'

#ToDo dynamisch täglich die Zeiten berechnen
start = '2021-01-01'
end = '2025-12-25'

#Get stock market data from Fraunhofer API
def fetch_stock_market_data():
    url = f'https://api.energy-charts.info/price?bzn=DE-LU&start={start}&end={end}'
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

def compute_total_price_composition(stock_data: dict)-> DataFrame:
    """
    Computes a dataframe containing the total price composition given the stock data.
    :param stock_data: The stock data to compute the price composition for.
    :return: The dataframe containing the total price composition given the stock data.
    """
    df_stock_data = DataFrame(stock_data)
    df_stock_data = df_stock_data[['unix_seconds', 'price', ]]

    # compute timestamps
    for i, row in df_stock_data.iterrows():
        df_stock_data.loc[i,"timestamp"] = datetime.fromtimestamp(df_stock_data.loc[i,"unix_seconds"],pytz.timezone("Europe/Berlin"))
    # calculate kWh from mWh
    df_stock_data['stock price'] = df_stock_data['price'] / 1000



    # Zusätzliche Abgaben
    df_stock_data['Nutzungsentgeld'] = [0.087] * len(df_stock_data['price'])
    df_stock_data['Sonstige Umlagen'] = [0.0188] * len(df_stock_data['price'])
    df_stock_data['Konzessionsabgabe'] = [0.0166] * len(df_stock_data['price'])
    df_stock_data['weitere Beschaffungskosten'] = [0.0215] * len(df_stock_data['price'])
    df_stock_data['additional costs'] = (df_stock_data['Nutzungsentgeld']
                                         + df_stock_data['Sonstige Umlagen']
                                         + df_stock_data['Konzessionsabgabe']
                                         + df_stock_data['weitere Beschaffungskosten'])

    # Steuern
    df_stock_data['Stromsteuer'] = [0.0205] * len(df_stock_data['price'])
    df_stock_data['Mehrwertsteuer'] = (df_stock_data['stock price']
                                       + df_stock_data['additional costs']
                                       + df_stock_data['Stromsteuer']) * 0.19
    df_stock_data['taxes'] = df_stock_data['Stromsteuer'] + df_stock_data['Mehrwertsteuer']


    # df_stock_data['gross price'] = (df_stock_data['stock price'] + 0.087 + 0.0205 + 0.0188 + 0.0166 + 0.0215) * 1.19
    df_stock_data['gross total'] = (df_stock_data['stock price']
                                               + df_stock_data['additional costs']
                                               + df_stock_data['taxes'])
    df_stock_data = df_stock_data.round(5)


    return df_stock_data

#write Data to InfluxDB Bucket
def write_to_influxdb(data: DataFrame):
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    #write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api = client.write_api()
    print(data)

    #ToDo optional, Felder wie in dem Bild zu sehen beschreiben, aus denen sich der Bruttopreis zusammensetzt
    #ToDo sinnvolle Bennenung der entsprechenden fields und Schreiben auf die InfluxDB wieder aktivieren

    # for item in [*data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['today'], *data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['tomorrow']]:
    for i, item in data.iterrows():
        point = Point("price_prediction") \
            .tag("entity_id", "energy_price_one_day_ahead") \
            .tag("_measurement", "€") \
            .field("total", item['gross total']) \
            .field("stock_price", item['stock price']) \
            .field("Nutzungsentgeld", item["Nutzungsentgeld"]) \
            .field("Sonstige Umlagen", item["Sonstige Umlagen"]) \
            .field('Konzessionsabgabe',item['Konzessionsabgabe']) \
            .field('weitere Beschaffungskosten', item['weitere Beschaffungskosten']) \
            .field('additional costs', item['additional costs']) \
            .field('Stromsteuer', item['Stromsteuer']) \
            .field('Mehrwertsteuer', item['Mehrwertsteuer']) \
            .field("taxes", item['taxes']) \
            .time(item["timestamp"], WritePrecision.NS)
        # ToDo --> field tax: wie oben bei optional beschrieben, können wir hier eine komplette Aufteilung machen oder einfach Abgaben summieren
        write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, point)
    #write_api.__del__()
    client.__del__()

if __name__ == '__main__':
    stock_data = fetch_stock_market_data()

    df_stock_data = compute_total_price_composition(stock_data)
    #ToDo in InfluxDB statt csv schreiben
    df_stock_data.to_csv('stock_data')
    print(df_stock_data)
    write_to_influxdb(df_stock_data)