from src.broker import Broker
import time
import threading
import zmq


class ReplayBroker(Broker):
    def __init__(self, local_replay_address, remote_replay_address, server_pub_address, edge_sub_address) -> None:
        """
        Initializes a ReplayBroker object.

        Args:
            local_replay_address (str): The address for the local replay socket.
            remote_replay_address (str): The address for the remote replay socket.
            server_pub_address (str): The address for the server publish socket.
            edge_sub_address (str): The address for the edge subscribe socket.
        """
        super().__init__(server_pub_address, edge_sub_address)
        self.local_replay_socket = self.context.socket(zmq.REP)
        self.local_replay_socket.bind(local_replay_address)

        self.remote_replay_socket = self.context.socket(zmq.REQ)
        self.remote_replay_socket.connect(remote_replay_address)

    def recv_replay_requests(self):
        """
        Receives replay requests from the client and sends the requested events.
        """
        while True:
            # Receive a message from the client
            request = self.local_replay_socket.recv_json()

            if request:
                request_type = request.get("type")

                if request_type == "replay_by_id":
                    events = self.get_event_by_id(request.get("last_event_id"))
                elif request_type == "replay_all":
                    events = self.get_all_events()

                self.local_replay_socket.send_json(events)

            # Wait for a short period before checking for new messages
            time.sleep(1)

    def send_replay_by_id_request(self):
        """
        Sends a replay by ID request to the remote replay socket.
        """
        last_event_id = "1234"
        self.remote_replay_socket.send_json({"type": "replay_by_id", "last_event_id": last_event_id})
        response = self.remote_replay_socket.recv_json()
        self.publish_events(response.get("events"))

    def send_replay_all_request(self):
        """
        Sends a replay all request to the remote replay socket.
        """
        self.remote_replay_socket.send_json({"type": "replay_all"})
        response = self.remote_replay_socket.recv_json()
        self.publish_events(response.get("events"))

    def publish_events(self, events):
        """
        Publishes events to the edge subscribe socket.

        Args:
            events (list): List of events to publish.
        """
        for event in events:
            print(event)
            # self.edge_sub_socket.send_json(event)


if __name__ == "__main__":
    broker1 = ReplayBroker(
        local_replay_address="tcp://127.0.0.1:4114",
        remote_replay_address="tcp://127.0.0.1:1234",
        server_pub_address="tcp://127.0.0.1:5559",
        edge_sub_address="tcp://127.0.0.1:5560",
    )
    broker2 = ReplayBroker(
        local_replay_address="tcp://127.0.0.1:1234",
        remote_replay_address="tcp://127.0.0.1:4114",
        server_pub_address="tcp://127.0.0.1:1111",
        edge_sub_address="tcp://127.0.0.1:2222",
    )
    threading.Thread(target=broker2.recv_replay_requests).start()
    threading.Thread(target=broker1.send_replay_all_request).start()