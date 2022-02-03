from pymongo import MongoClient
import json

class DBClient():
    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        try:
            self.client.admin.command('ismaster')
            print("Connected")
            self.db = self.client["bhavcopy"]
        except Exception as e:
            print("Unable to connect. Exception :%s", str(e))

    def get_bse100(self):
        try:
            return [record["bse100"] for record in self.db["bse100"].find()][0]
        except Exception as e:
            print("Could not get Record")
    def insert_bhavcopy(self, date, data):
        record = {"date": date, "data": json.dumps(data)}
        collection = self.db["bhavcopy"]
        try:
            collection.insert_one(record)
        except Exception as e:
            print(str(e))

    def get_bhavcopy(self, date):
        collection = self.db["bhavcopy"]
        try:
            return json.loads(collection.find_one({"date": date})["data"])
        except Exception as e:
            print("Could not get Record")
