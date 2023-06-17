import zmq
import time
from datetime import datetime
import random
import uuid
import json
import yaml
import os

def generate_electricity_rows() -> dict:
    while True:
        date = datetime.now()
        ev_usage = round(random.uniform(0, random.uniform(100, 1000)), 2)
        uuid_value = uuid.uuid1()
        yield {"date": date, "uuid":uuid_value, "ev_usage": ev_usage}

class Sensor:

    def __init__(self, socket_address, delay=0.3) -> None:
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB) 
        self.publisher.bind(socket_address)  # Connect socket to backend of the broker
        self.delay = delay

    def start(self):
        data_generator = generate_electricity_rows()
        for data in data_generator:
            self.publish_data(data)
            time.sleep(self.delay)
    
    def publish_data(self, json_data: dict):
        data = json.dumps(json_data, indent=4, sort_keys=True, default=str)
        # print(data)
        self.publisher.send_json(data) # Send message to subscribers

    
if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../configs/sensor.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    sensor = Sensor(socket_address=config["socket"], delay=config["delay"])
    sensor.start()