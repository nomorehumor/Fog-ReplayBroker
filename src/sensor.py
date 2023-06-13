import zmq
import time
from datetime import datetime
import random
import uuid
import json

def generate_electricity_rows() -> dict:
    while True:
        date = datetime.now()
        ev_usage = round(random.uniform(0, random.uniform(100, 1000)), 2)
        time.sleep(0.3)
        uuid_value = uuid.uuid1()
        yield {"date": date, "uuid":uuid_value, "ev_usage": ev_usage}

class Sensor:

    def __init__(self, socket_address) -> None:
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.REQ) 
        self.publisher.connect(socket_address)  # Connect socket to backend of the broker

    def start(self):
        data_generator = generate_electricity_rows()
        for data in data_generator:
            self.publish_data(data)
    
    def publish_data(self, json_data: dict):
        data = json.dumps(json_data, indent=4, sort_keys=True, default=str)
        print(data)
        self.publisher.send_json(data) # Send message to subscribers

    
if __name__ == "__main__":
    sensor = Sensor(socket_address="tcp://127.0.0.1:5560")
    sensor.start()