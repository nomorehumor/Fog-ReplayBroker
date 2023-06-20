from pymongo import MongoClient
from queue import Queue

class Repository:
    def __init__(self, db_url: str, queue_size: int) -> None:
        self.client = MongoClient(db_url)
        self.energy_collection = self.client["sensor-data"]["energy_data"]
        self.energy_data_cache = Queue(queue_size)

        
    def insert_energy_value(self, value):
        self.energy_collection.insert_one(value)
    
    # def find_after_timestamp
            
if __name__ == "__main__":
    repo = Repository("mongodb://localhost:27017/")
    repo.insert({"keyone": 1, "keytwo": 2})