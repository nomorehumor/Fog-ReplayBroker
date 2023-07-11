import zmq
import time
from datetime import datetime
import random
import uuid
import json
import yaml
import os
import argparse

DATA_ENERGY_USAGE = "energy_usage"
DATA_WEATHER = "weather"
DATA_ENERGY_GENERATION = "energy_generation"

TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def generate_electricity_rows() -> dict:
    while True:
        date = datetime.now()
        ev_usage = round(random.uniform(0, random.uniform(100, 1000)), 2)
        uuid_value = uuid.uuid1()
        yield {"timestamp": date.strftime(TIME_FORMAT), "uuid": str(uuid_value), "name": DATA_ENERGY_USAGE, "value": ev_usage}

def generate_weather_rows() -> dict:
    while True:
        date = datetime.now()
        temperature = round(random.uniform(-10, 40), 2)
        humidity = round(random.uniform(0, 100), 2)
        wind_speed = round(random.uniform(0, 30), 2)
        uuid_value = uuid.uuid1()
        yield {"timestamp": date.strftime(TIME_FORMAT), "uuid": str(uuid_value), "name": DATA_WEATHER, "temperature": temperature, "humidity": humidity, "wind_speed": wind_speed}

def generate_energy_generation_rows() -> dict:
    while True:
        date = datetime.now()
        energy_generation = round(random.uniform(0, random.uniform(1, 5)), 4)
        uuid_value = uuid.uuid1()
        yield {"timestamp": date.strftime(TIME_FORMAT), "uuid": str(uuid_value), "name": DATA_ENERGY_GENERATION, "value": energy_generation}
class DataProvider:

    def __init__(self, socket_address, delay=0.3) -> None:
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB) 
        self.publisher.connect(socket_address)  # Connect socket to backend of the broker
        self.delay = delay

    def start(self, data_type):
        if data_type == DATA_ENERGY_USAGE:
            data_generator = generate_electricity_rows()
        elif data_type == DATA_WEATHER:
            data_generator = generate_weather_rows()
        elif data_type == DATA_ENERGY_GENERATION:
            data_generator = generate_energy_generation_rows()
            
        for data in data_generator:
            self.publish_data(data)
            time.sleep(self.delay)
    
    def publish_data(self, json_data: dict):
        data = json.dumps(json_data, indent=4, sort_keys=True, default=str)
        print(data)
        self.publisher.send_json(json_data) # Send message to subscribers

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default=os.path.dirname(os.path.realpath(__file__)) + "/configs/sensor_fog.yaml")
    parser.add_argument("-t", "--type", type=str, required=True, help=f"Options: {DATA_ENERGY_USAGE}, {DATA_WEATHER}, {DATA_ENERGY_GENERATION}")
    args = parser.parse_args()
    
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
        
    sensor = DataProvider(socket_address=config["socket"], delay=config["delay"])
    sensor.start(args.type)