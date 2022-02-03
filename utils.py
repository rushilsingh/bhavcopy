import json
import os
import requests
import io
import zipfile
import datetime
import pytz
from db_client import DBClient

bhavcopy_client = DBClient(os.environ.get("MONGO_URL"))
BASE_FNAME = "EQ{}.CSV"
BASE_URL = "https://www.bseindia.com/download/BhavCopy/Equity/EQ{}_CSV.ZIP"


def download(date):

    header = "Date: " + date
    date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d%m%y')

    table_header = ["Code", "Name", "Open", "Close", "High",
                    "Low", "Previous Close", "Change"]
    output = bhavcopy_client.get_bhavcopy(date)
    if output:
        print("From DB")
        return {"output": output, "header": header, "table_header": table_header}
    else:
        print("No entry in DB. Downloading fresh copy")
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
            output = parse(text)
        else:
            output = {}
        if output:
            bhavcopy_client.insert_bhavcopy(date, output)


        return {"output": output, "header": header, "table_header": table_header}


def parse(text):

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
        record = {"Name": name, "Open": open_value, "Close": close_value,
                  "High": high_value, "Low": low_value, "Previous Close": prevclose, "Code": sc_code}
        records.append(record)
    parsed = []
    invalids = []
    for record in records:
        name = record["Name"]
        close_value = float(record["Close"])
        prevclose_value = float(record["Previous Close"])
        diff = close_value - prevclose_value
        name = "\"" + name + "\"" if " " in name else name
        try:
            diff = (diff/prevclose_value) * 100.00000
            record["Change"] = diff
        except Exception as e:
            record["Change"] = "NA"
            invalids.append(record)
        else:
            parsed.append(record)

    parsed = sorted(parsed, key=lambda k: k.get("Change"), reverse=True)
    for record in parsed:
        record["Change"] = "%.2f %%" % record["Change"]
    parsed.extend(invalids)

    return parsed
