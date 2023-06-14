import zmq

class Broker:
    def __init__(self, server_pub_address, edge_sub_address) -> None:
        self.context = zmq.Context()
        self.edge_sub_socket = self.context.socket(zmq.SUB)  # XSUB socket for receiving messages from multiple publishers
        self.edge_sub_socket.connect(edge_sub_address)  # Bind frontend socket to port 5560
        self.edge_sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
        
        self.server_pub_socket = self.context.socket(zmq.XPUB)
        self.server_pub_socket.bind(server_pub_address)  # Bind backend socket to port 5559

    def get_event_by_id(self, last_event_id):
        return {"events": [{"id": 1, "date": "2021-10-10", "uuid": "1234", "ev_usage": 1234}] }

    def get_all_events(self):
        return {"events": [{"id": 1, "date": "2021-10-10", "uuid": "1234", "ev_usage": 1234}] }

    def poll(self):
        while True:
            print("waiting for msg")
            message = self.edge_sub_socket.recv_json()
            print(message)

if __name__ == "__main__":
    broker = Broker(
        server_pub_address="tcp://127.0.0.1:5559",
        edge_sub_address="tcp://127.0.0.1:5560",
    )
    broker.poll()