import zmq
import os
import yaml
class Subscriber:
    def __init__(self, sub_socket) -> None:
        self.sub_socket = sub_socket
        
        self.context = zmq.Context()
        self.edge_sub_socket = self.context.socket(zmq.SUB) 
        self.edge_sub_socket.connect(sub_socket)
        self.edge_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
    
    def start(self):
        while True:
            data = self.edge_sub_socket.recv_json()
            print(data)
    

if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + "/configs/subscriber.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    subscriber = Subscriber(config["sub_socket"])
    subscriber.start()