import json
import os
import requests
import io
import zipfile
import datetime
import textfsm
import pytz

BASE_FNAME = "EQ{}.CSV"
BASE_URL = "https://www.bseindia.com/download/BhavCopy/Equity/EQ{}_CSV.ZIP"

def download(date):

        url = BASE_URL.format(date)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) '
                     'Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

        response = requests.get(url, headers=headers)
        fname = BASE_FNAME.format(date)

        if response and response.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(response.content))
            z.extractall()
            with open(fname) as f:
                text = f.read()
            os.unlink(fname)
            return parse(text, date)

        return {}

def parse(text, date):

        lines = text.split("\n")
        header = lines[0]
        header = header.split(",")
        lines = lines[1:]
        lines = [line for line in lines if line]
        name_index = header.index("SC_NAME")
        open_index = header.index("OPEN")
        close_index = header.index("CLOSE")
        high_index = header.index("HIGH")
        low_index = header.index("LOW")
        prevclose_index = header.index("PREVCLOSE")
        code_index = header.index("SC_CODE")
        records = []
        lines = [line for line in lines if line]
        for line in lines:
            fields = line.split(",")
            name = fields[name_index]
            open_value = fields[open_index]
            close_value = fields[close_index]
            high_value = fields[high_index]
            low_value = fields[low_index]
            prevclose = fields[prevclose_index]
            sc_code = fields[code_index]
            record = {"Name": name, "Open": open_value, "Close": close_value, "High": high_value, "Low": low_value, "Previous Close": prevclose, "Code": sc_code}
            records.append(record)
        diffs = []
        parsed = []
        for record in records:
            name = record["Name"]
            close_value = float(record["Close"])
            prevclose_value = float(record["Previous Close"])
            diff = close_value - prevclose_value
            diff = (diff/close_value) * 100.00000
            name = "\"" + name + "\"" if " " in name else name
            record["Change Percentage"] = "%.2f " % diff  + " %"
            diffs.append(diff)
            parsed.append(record)
        return parsed


