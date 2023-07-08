from typing import Deque
import uuid
import pymongo
from pymongo import MongoClient
from queue import Queue
import datetime

class Repository:
    def __init__(self, db_url: str, queue_size: int) -> None:
        self.client = MongoClient(db_url)
        self.energy_collection = self.client["sensor-data"]["energy_data"]
        self.energy_data_cache = Deque(maxlen=queue_size)

    def insert_energy_value(self, msg):
        persist_object = {
            "arrival_time": msg["arrival_time"],
            "timestamp": msg["timestamp"],
            "_id": msg["uuid"],
            "value": msg["value"]
        }
                
        self.energy_collection.insert_one(persist_object)
        self.energy_data_cache.put(persist_object)
    
    def find_energy_by_id(self, id):
        return self.energy_collection.find_one({"_id": id})
    
    def find_energy_after_arrival_time(self, timestamp: datetime.datetime):
        return list(self.energy_collection.find({"arrival_time": {"$gt": timestamp}}))
    
    def get_latest_energy_usage(self):
        latest_entry = list(self.energy_collection.find().sort("arrival_time", pymongo.DESCENDING).limit(1))
        if latest_entry == []:
            return None
        return latest_entry[0]
    
    def get_energy_all(self):
        return list(self.energy_collection.find())
            
if __name__ == "__main__":
    repo = Repository("mongodb://localhost:27017/", 10)
    id = str(uuid.uuid1())
    repo.insert_energy_value({"timestamp": datetime.datetime.now(), "arrival_time": datetime.datetime.now(), "uuid": id, "value": 228.0})
    print(repo.find_energy_by_id(id))
    print(repo.find_energy_after_arrival_time(datetime.datetime(2023, 6, 29, 12, 9, 41, 243000)))