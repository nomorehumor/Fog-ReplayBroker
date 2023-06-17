import zmq
import os
import yaml

class Broker:
    def __init__(self, sub_socket, pub_socket) -> None:
        self.context = zmq.Context()
        self.edge_sub_socket = self.context.socket(zmq.SUB)  # XSUB socket for receiving messages from multiple publishers
        self.edge_sub_socket.connect(sub_socket)  # Bind frontend socket to port 5559
        self.edge_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
        
        self.server_pub_socket = self.context.socket(zmq.XPUB)
        self.server_pub_socket.bind(pub_socket)  # Bind backend socket to port 5560
    
    def poll(self):
        while True:
            print("waiting for msg")
            message = self.edge_sub_socket.recv_json()
            print("Received:", message)
    
if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../configs/broker.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    broker = Broker(sub_socket=config["sub_socket"], pub_socket=config["pub_socket"])
    broker.poll()