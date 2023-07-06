import os
from sensor.sensor import Sensor
from replay_broker.broker import Broker
import yaml
from multiprocessing import Process

def start_sensor():
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../configs/sensor.yaml", "r") as f:
        sensor_config = yaml.safe_load(f)
    sensor = Sensor(socket_address=sensor_config["socket"], delay=sensor_config["delay"])
    sensor.start()
    
def start_broker():
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../configs/broker.yaml", "r") as f:
        broker_config = yaml.safe_load(f)
    broker = Broker(sub_socket=broker_config["sub_socket"], pub_socket=broker_config["pub_socket"])
    broker.poll()
    

if __name__ == "__main__":
    sensor_process = Process(target=start_sensor)
    broker_process = Process(target=start_broker)
    
    sensor_process.start()
    broker_process.start()

    sensor_process.join()
    broker_process.join()