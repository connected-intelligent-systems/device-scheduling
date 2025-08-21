import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import paramiko


def connect_to_server():

    router_ip = "192.168.1.8"
    router_username = "k8s"
    router_password = "k8s"

    ssh = paramiko.SSHClient()

    # Load SSH host keys.
    ssh.load_system_host_keys()
    # Add SSH host key automatically if needed.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to router using username/password authentication.
    ssh.connect(router_ip,
                username=router_username,
                password=router_password,
                look_for_keys=False)
    return ssh

    # Run command.
    # ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("show ip route")
    #
    # output = ssh_stdout.readlines()
    # print(output)
    # # Close connection.
    # ssh.close()
    #
    # # Analyze show ip route output
    # for line in output:
    #     if "0.0.0.0/0" in line:
    #         print("Found default route:")
    #         print(line)


def configure_user():
    # token = os.environ.get("INFLUXDB_TOKEN")
    token = '1R4LfbMgsv9wb6zl7NOosmiYnDJuZRsaXS8yrK6zrDDFdge6lENrXnTpD60kQ8HhY3-FsO2WMJ89Y6xjLxaAEg=='
    org = "homeassist"
    # url = "http://asr-demo6-usg.sb.dfki.de/ec9cbdb7_influxdb2/ingress"
    url = "http://192.168.1.8:8086"

    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    return write_client


def get_time_series():
    client = configure_user()

    query_api = client.query_api()

    query = """import "interpolate"
               from(bucket: "homeassist")
                 |> range(start: 2025-04-27T00:00:00Z, stop: 2025-04-28T00:00:00Z)
                 |> filter(fn: (r) => r["_measurement"] == "price_prediction")
                 |> aggregateWindow(every: 15m, fn: mean, createEmpty: false)
                 |> interpolate.linear(every: 15m)  
                 |> yield(name: "mean")"""
    tables = query_api.query(query, org="homeassist")


    for table in tables:
        for record in table.records:
            print(record)


if __name__ == '__main__':
    # ssh_client = connect_to_server()
    get_time_series()
    # ssh_client.close()