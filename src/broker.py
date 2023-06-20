import zmq
import os
import yaml
from queue import Queue
import datetime

from persistance import Repository

class Broker:
    def __init__(self, sub_socket: str, pub_socket: str, db_url: str, queue_size: int = 500) -> None:
        self.context = zmq.Context()
        
        # Edge socket for incoming sensor messages
        self.edge_sub_socket = self.context.socket(zmq.SUB)  # XSUB socket for receiving messages from multiple publishers
        self.edge_sub_socket.connect(sub_socket)  # Bind frontend socket to port 5559
        self.edge_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
        
        # Server socket for outgoing messages to cloud
        self.server_pub_socket = self.context.socket(zmq.XPUB)
        self.server_pub_socket.bind(pub_socket)  # Bind backend socket to port 5560
        
        # Persistance
        self.repository = Repository(db_url, queue_size)
    
    def process_msg(self, msg: dict):
        persist_object = {
            "arrival_time": datetime.datetime.now(),
            "timestamp": msg["timestamp"],
            "_id": msg["uuid"],
        }
        
        if msg["name"] == "energy_usage":
            persist_object["value"] = msg["value"]
            self.energy_data_cache.put(persist_object)
            self.repository.insert_energy_value(persist_object)
    
    def poll(self):
        while True:
            print("Waiting for msg")
            message = self.edge_sub_socket.recv_json()
            self.process_msg(message)
            print("Received:", message)
    
if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../configs/broker.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    broker = Broker(
        sub_socket=config["sub_socket"], 
        pub_socket=config["pub_socket"], 
        db_url=config["db_url"], 
        queue_size=config["queue_size"]
        )
    broker.poll()