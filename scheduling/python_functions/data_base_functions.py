import re
from datetime import datetime, timezone, tzinfo, timedelta


import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.flux_table import FluxTable
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd
from problog.extern import problog_export

from scheduling.python_functions.problog_functions_utils import reformat_problog_predicates


def convert_timedelta_to_timespan_string(time_span: datetime) -> str:
    """
    Converts a timedelta object to a influxDB compatible time span string.
    :param time_span: The time span to be converted.
    :return: An influxDB compatible string representation of the time span.
    """
    timespan_string = ""

    if time_span.hour > 0:
        timespan_string += str(time_span.hour) + "h"
    if time_span.minute > 0:
        timespan_string += str(time_span.minute) + "m"
    if time_span.second > 0:
        timespan_string += str(time_span.second) + "s"
    return timespan_string


def influxdb_setup():
    """
    Setup for the InfluxDB setup.
    :return: The client to use for InfluxDB operations.
    """
    # token = os.environ.get("INFLUXDB_TOKEN")
    token = '1R4LfbMgsv9wb6zl7NOosmiYnDJuZRsaXS8yrK6zrDDFdge6lENrXnTpD60kQ8HhY3-FsO2WMJ89Y6xjLxaAEg=='
    # token = 'e52NKvX_G__hxPPDlzFt5TwgRs0BAX_LHpmJOw9PrbxqpuPUAwoDShVA8BBXcsSvfUsoLeHMcai9uOYbF5Re-Q=='
    org = "homeassist"
    # url = "http://asr-demo6-usg.sb.dfki.de/ec9cbdb7_influxdb2/ingress"
    # url = "http://192.168.1.8:8086"
    url = "http://localhost:8086"

    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org,timeout=10_000)
    return write_client


@problog_export('-list')
def get_energy_price_prediction(time_density, start_time = None, prediction_window = None) -> list:
    """
    Returns the energy price prediction as list with time intervals time_density starting at start_time for a timespan
    given by prediction_window.
    :param time_density: The time interval between two timepoints of the prediction.
    :param start_time: The start time for the prediction.
    :param prediction_window: The amount of time captured in the prediction.
    :return: The predicted energy price for the time window.
    """

    time_density = reformat_problog_predicates([time_density])

    dt = datetime.strptime(time_density, "%H:%M:%S")
    time_density_str = convert_timedelta_to_timespan_string(dt)

    client = influxdb_setup()

    query_api = client.query_api()

    query = """import "interpolate"
               from(bucket: "homeassist")
                 |> range(start: 2025-04-27T00:00:00Z, stop: 2025-04-28T00:00:00Z)
                 |> filter(fn: (r) => r["_measurement"] == "price_prediction")
                 |> aggregateWindow(every: """ + time_density_str + """, fn: mean, createEmpty: false)
                 |> interpolate.linear(every: """+ time_density_str + """)  
                 |> yield(name: "mean")"""

    query_table = query_api.query_data_frame(query, org="homeassist")

    prediction_table = query_table.where(query_table["_field"] == "total").dropna()

    prediction = list(prediction_table["_value"])

    return prediction


if __name__ == '__main__':
    prediction = get_energy_price_prediction('00:15:00')
    print(prediction)
