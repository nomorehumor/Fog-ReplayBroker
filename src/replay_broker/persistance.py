from typing import Deque
import uuid
import pymongo
from pymongo import MongoClient
from queue import Queue
from datetime import datetime


class Repository:
    def __init__(self, db_url: str, queue_size: int) -> None:
        self.client = MongoClient(db_url)
        self.db = self.client["sensor-data"]
        # self.energy_collection = self.client["sensor-data"]["energy_data"]
        # self.weather_collection = self.client["sensor-data"]["weather"]

    def insert_value(self, msg, collection: str):
        persist_object = self._create_persist_object(msg)      
        self.db[collection].insert_one(persist_object)
    
    def find_data_by_id(self, id, collection: str):
        return self.db[collection].find_one({"_id": id})
    
    def find_data_after_arrival_time(self, arrival_time: datetime, collection: str):
        return list(map(self._create_energy_msg_object, list(self.db[collection].find({"arrival_time": {"$gt": arrival_time}}))))

    def find_data_after_id(self, id: str, collection: str):
        element = self.db[collection].find_one({"_id": id})
        return list(map(self._create_energy_msg_object, self.find_data_after_arrival_time(element["arrival_time"])))
    
    def find_latest_data(self, collection: str):
        latest_entry = list(self.db[collection].find().sort("arrival_time", pymongo.DESCENDING).limit(1))
        if latest_entry == []:
            return None
        return self._create_energy_msg_object(latest_entry[0])
    
    def get_data_all(self, collection: str):
        return list(map(self._create_energy_msg_object, list(self.db[collection].find())))
    
    def _create_persist_object(self, msg):
        if msg["name"] == "energy_usage":
            persist_object = {
                "arrival_time": msg["arrival_time"],
                "timestamp": msg["timestamp"],
                "_id": msg["uuid"],
                "value": msg["value"],
                "name": msg["name"]
            }
        elif msg["name"]  == "weather":
            persist_object = {
                "arrival_time": msg["arrival_time"],
                "timestamp": msg["timestamp"],
                "_id": msg["uuid"],
                "temperature": msg["temperature"],
                "humidity": msg["humidity"],
                "wind_speed": msg["wind_speed"],
                "name": msg["name"]
            }
        elif msg["name"]  == "energy_generation":
            persist_object = {
                "arrival_time": msg["arrival_time"],
                "timestamp": msg["timestamp"],
                "_id": msg["uuid"],
                "value": msg["value"],
                "name": msg["name"]
            }
        return persist_object

    def _create_energy_msg_object(self, persist_object):
        if persist_object["name"] == "energy_usage":
            msg = {
                "arrival_time": persist_object["arrival_time"],
                "timestamp": persist_object["timestamp"],
                "uuid": persist_object["_id"],
                "value": persist_object["value"],
                "name": persist_object["name"]
            }
        elif persist_object["name"]  == "weather":
            msg = {
                "arrival_time": persist_object["arrival_time"],
                "timestamp": persist_object["timestamp"],
                "uuid": persist_object["_id"],
                "temperature": persist_object["temperature"],
                "humidity": persist_object["humidity"],
                "wind_speed": persist_object["wind_speed"],
                "name": persist_object["name"]
            }
        elif persist_object["name"]  == "energy_generation":
            msg = {
                "arrival_time": persist_object["arrival_time"],
                "timestamp": persist_object["timestamp"],
                "uuid": persist_object["_id"],
                "value": persist_object["value"],
                "name": persist_object["name"]
            }
        return msg
            
if __name__ == "__main__":
    repo = Repository("mongodb://localhost:27017/", 10)
    id = str(uuid.uuid1())
    repo.insert_value({"timestamp": datetime.datetime.now(), "arrival_time": datetime.datetime.now(), "uuid": id, "value": 228.0}, "energy_usage")
    print(repo.find_data_by_id(id))
    print(repo.find_energy_after_arrival_time(datetime.datetime(2023, 6, 29, 12, 9, 41, 243000)))