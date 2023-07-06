import zmq

class Subscriber:
    def __init__(self, pub_ip, sub_socket) -> None:
        self.pub_ip = pub_ip
        self.sub_socket = sub_socket
        
        self.edge_sub_socket = self.context.socket(zmq.SUB) 
    
    def send_subscribe_request(self):
        pass