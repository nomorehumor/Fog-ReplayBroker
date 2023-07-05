from broker import Broker
import time
import threading
import zmq
import os
import yaml


class ReplayBroker(Broker):
    def __init__(self, sub_socket: str, pub_socket: str, db_url: str, queue_size: int, replay_socket) -> None:
        """
        Initializes a ReplayBroker object.

        Args:
            local_replay_address (str): The address for the local replay socket.
            remote_replay_address (str): The address for the remote replay socket.
            server_pub_address (str): The address for the server publish socket.
            edge_sub_address (str): The address for the edge subscribe socket.
        """
        super().__init__(sub_socket, pub_socket, db_url)
        # create local replay server
        self.local_replay_socket = self.context.socket(zmq.REP)
        self.local_replay_socket.bind(replay_socket)
        self.last_event_date = None
        # The address for the remote replay socket.
        self.remote_replay_socket = None
        self.request_in_progress = False
        self.send_replay_lock = threading.Lock()
        self.first_event_date = None

    def connect_to_remote_replay_server(self, remote_replay_address):
        """
        Connects to the remote replay server.
        """
        self.remote_replay_address = remote_replay_address

    def start_local_replay_server(self):
        """
        Receives replay requests from the client and sends the requested events.
        """
        while True:

            # Receive a message from the client
            request = self.local_replay_socket.recv_json()

            if request:
                request_type = request.get("type")

                if request_type == "replay_by_timestamp":
                    events = self.get_event_by_id(request.get("last_event_date"))
                elif request_type == "replay_all":
                    events = self.get_all_events()

                print("send response", events)
                self.local_replay_socket.send_json(events)
                self.first_run = False

            # Wait for a short period before checking for new messages
            time.sleep(1)

    def start_replay_request_loop(self, interval=2, timeout=5):
        while True:
            if not self.request_in_progress:  # Only send a new request if one is not already in progress
                self.send_replay_request(timeout)
            time.sleep(interval)

    def send_replay_request(self, timeout):
        if self.last_event_date is None:
            request = {"type": "replay_all"}
        else:
            request = {"type": "replay_by_timestamp", "last_event_date": self.last_event_date}

        with self.send_replay_lock:
            self.request_in_progress = True  # Set the flag to indicate that a request is in progress
            threading.Thread(target=self._send_replay_request, args=(request, timeout)).start()

    def _send_replay_request(self, request, timeout):

        # Create connection to remote replay server
        self.remote_replay_socket = self.context.socket(zmq.REQ)
        self.remote_replay_socket.connect(self.remote_replay_address)

        # Send the replay request to the remote replay server
        print("Sending replay request")
        self.remote_replay_socket.send_json(request)

        # Create poller to check for timeout
        poller = zmq.Poller()
        poller.register(self.remote_replay_socket, zmq.POLLIN)

        # Wait for a response from the remote replay server
        if poller.poll(timeout=timeout * 1000):
            print("Trying to receive response")
            response = self.remote_replay_socket.recv_json()
            print(response)
            # self.publish_events(response.get("events"))
        else:
            print("Timeout occurred, handling the timeout event")
            self.remote_replay_socket.close()

        self.request_in_progress = False

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
    with open(os.path.dirname(os.path.realpath(__file__)) + "/../configs/fog_broker.yaml", "r") as f:
        fog_config = yaml.safe_load(f)

    with open(os.path.dirname(os.path.realpath(__file__)) + "/../configs/cloud_broker.yaml", "r") as f:
        cloud_config = yaml.safe_load(f)

    fogBroker = ReplayBroker(
        sub_socket=fog_config["sub_socket"],
        pub_socket=fog_config["pub_socket"],
        db_url=fog_config["db_url"],
        queue_size=fog_config["queue_size"],
        replay_socket=fog_config["replay_socket"]
    )
    cloudBroker = ReplayBroker(
        sub_socket=cloud_config["sub_socket"],
        pub_socket=cloud_config["pub_socket"],
        db_url=fog_config["db_url"],
        queue_size=cloud_config["queue_size"],
        replay_socket=cloud_config["replay_socket"]
    )

    fogBroker.connect_to_remote_replay_server(cloud_config["replay_socket"])

    threading.Thread(target=cloudBroker.start_local_replay_server).start()
    threading.Thread(target=fogBroker.start_replay_request_loop).start()
