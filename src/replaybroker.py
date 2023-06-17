from broker import Broker
import time
import threading
import zmq


class ReplayBroker(Broker):
    def __init__(self, local_replay_address, server_pub_address, edge_sub_address) -> None:
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

        self.last_event_id = None

    def connect_to_remote_replay_server(self, remote_replay_address):
        """
        Connects to the remote replay server.
        """
        self.remote_replay_socket = self.context.socket(zmq.REQ)
        self.remote_replay_socket.connect(remote_replay_address)

    def start_replay_server(self):
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

    def send_replay_request(self):
        if self.remote_replay_socket is None:
            raise Exception("Not connected to remote replay server")

        if self.last_event_id is None:
            request = {"type": "replay_all"}
        else:
            request = {"type": "replay_by_id", "last_event_id": self.last_event_id}

        self.remote_replay_socket.send_json(request)
        response = self.remote_replay_socket.recv_json()
        self.publish_events(response.get("events"))

    def publish_events(self, events):
        """
        Publishes events to the edge subscribe socket.

        Args:
            events (list): List of events to publish.
        """
        # TODO: Add logic to publish events to the edge subscribe socket.
        # TODO: set last_event_id
        for event in events:
            print(event)
            # self.edge_sub_socket.send_json(event)


if __name__ == "__main__":
    fogBroker = ReplayBroker(
        local_replay_address="tcp://127.0.0.1:4114",
        server_pub_address="tcp://127.0.0.1:5559",
        edge_sub_address="tcp://127.0.0.1:5560",
    )
    cloudBroker = ReplayBroker(
        local_replay_address="tcp://127.0.0.1:1234",
        server_pub_address="tcp://127.0.0.1:1111",
        edge_sub_address="tcp://127.0.0.1:2222",
    )

    fogBroker.connect_to_remote_replay_server("tcp://127.0.0.1:1234")

    threading.Thread(target=cloudBroker.start_replay_server).start()
    threading.Thread(target=fogBroker.send_replay_request).start()