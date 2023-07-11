import zmq
import os
import yaml
import datetime
import logging

from replay_broker.persistance import Repository
from replay_broker.serialization import serialize_msg, deserialize_msg, deserialize_timestamp

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Broker:
    def __init__(self, sub_socket: str, pub_socket: str, db_url: str, queue_size: int = 500) -> None:
        self.context = zmq.Context()
        
        # Edge socket for incoming sensor messages
        self.edge_sub_socket = self.context.socket(zmq.SUB)  # XSUB socket for receiving messages from multiple publishers
        self.edge_sub_socket.bind(sub_socket)  # Bind frontend socket to port 5559
        self.edge_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
        
        # Server socket for outgoing messages to cloud
        self.edge_pub_socket = self.context.socket(zmq.XPUB)
        self.edge_pub_socket.bind(pub_socket)  # Bind backend socket to port 5560
        
        # Persistance
        self.repository = Repository(db_url, queue_size)
    
    def process_pub_msg(self, msg: dict):
        msg["arrival_time"] = str(datetime.datetime.now())
        msg_deserialized = deserialize_msg(msg)

        self.repository.insert_value(msg_deserialized, msg_deserialized["name"])
        
        self.edge_pub_socket.send_json(msg)
    
    def poll(self):
        while True:
            message = self.edge_sub_socket.recv_json()
            self.process_pub_msg(message)
            logging.info(f"Received Sensor Data: {message}")
    
if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + "/configs/broker.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    broker = Broker(
        sub_socket=config["sub_socket"], 
        pub_socket=config["pub_socket"], 
        db_url=config["db_url"], 
        queue_size=config["queue_size"]
        )
    broker.poll()