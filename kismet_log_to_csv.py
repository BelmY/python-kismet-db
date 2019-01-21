#!/usr/bin/env python2

import argparse
import datetime
import os
import sqlite3
import sys
import csv

import kismetdb

try:
    from dateutil import parser as dateparser
except Exception as e:
    print("kismet_log_to_kml requires dateutil; please install it either via your distribution")
    print("(python-dateutil) or via pip (pip install dateutil)")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Kismet to CSV Log Converter")
parser.add_argument("--in", action="store", dest="infile", help='Input (.kismet) file')
parser.add_argument("--out", action="store", dest="outfile", help='Output CSV filename')
parser.add_argument("--table", action="store", dest="srctable", help='Select the table to output')

results = parser.parse_args()
replacements = {}

if results.infile is None:
    print("Expected --in [file]")
    sys.exit(1)

if not os.path.isfile(results.infile):
    print("Could not find input file '{}'".format(results.infile))
    sys.exit(1)

table = ""
if results.srctable is None:
    results.srctable = "devices"
replacements["srctable"] = results.srctable

if results.srctable == "devices":
    table_abstraction = kismetdb.Devices(results.infile)
    column_names = ["first_time", "last_time", "devkey", "phyname", "devmac",
                    "strongest_signal", "min_lat", "min_lon", "max_lat",
                    "max_lon", "avg_lat", "avg_lon", "bytes_data", "type"]
elif results.srctable == "packets":
    table_abstraction = kismetdb.Packets(results.infile)
    column_names = ["ts_sec", "ts_usec", "phyname", "sourcemac", "destmac",
                    "transmac", "frequency", "devkey", "lat", "lon",
                    "packet_len", "signal", "datasource", "dlt", "error"]
elif results.srctable == "datasources":
    table_abstraction = kismetdb.DataSources(results.infile)
    column_names = ["uuid", "typestring", "definition", "name", "interface"]
elif results.srctable == "alerts":
    table_abstraction = kismetdb.Alerts(results.infile)
    column_names = ["ts_sec", "ts_usec", "phyname", "devmac", "lat",
                    "lon", "header"]
else:
    print("Invalid table entered, please retry with either devices, packets, datasources or alerts.")
    sys.exit(1)

if results.outfile is None:
    results.outfile = "{}-{}.csv".format(results.infile, replacements["srctable"])


with open(results.outfile, 'wb') as csvfile:
    csvWriter = csv.DictWriter(csvfile, delimiter='\t', extrasaction="ignore",
                               fieldnames=column_names)
    nrows = 0
    csvWriter.writeheader()
    for row in table_abstraction.get_meta():
        csvWriter.writerow(row)
        nrows = nrows + 1
        if nrows % 1000 == 0:
            print("Wrote {} rows".format(nrows))
