import argparse
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

                self.local_replay_socket.send_json(events)

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
        try:
            # Create connection to remote replay server
            self.remote_replay_socket = self.context.socket(zmq.REQ)
            self.remote_replay_socket.setsockopt(zmq.CONNECT_TIMEOUT, timeout * 1000)
            self.remote_replay_socket.setsockopt(zmq.RCVTIMEO, timeout * 1000)
            self.remote_replay_socket.connect(self.remote_replay_address)

            # Send the replay request to the remote replay server
            print("Sending replay request", request.get("type"))
            self.remote_replay_socket.send_json(request)
            response = self.remote_replay_socket.recv_json()
            self.handle_events(response)
        except zmq.error.Again:
            print("Resource temporarily unavailable. Retrying in 5 sec later...")
            time.sleep(5)
            # Handle the temporary unavailability, such as adding a delay and retrying later
        finally:
            self.remote_replay_socket.close()
            self.request_in_progress = False

    def handle_events(self, events):
        for event in events:
            print(event)
            # TODO: handle event e.g. save into database


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default=os.path.dirname(os.path.realpath(__file__)) + "/configs/cloud_broker.yaml")
    parser.add_argument("-r", "--replay", default=False, action="store_true")
    args = parser.parse_args()
    
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    
    broker = ReplayBroker(
        sub_socket=config["sub_socket"],
        pub_socket=config["pub_socket"],
        db_url=config["db_url"],
        queue_size=config["queue_size"],
        replay_socket=config["replay_socket"]
    )
    
    if args.replay:
        threading.Thread(target=broker.start_replay_request_loop).start()
        broker.connect_to_remote_replay_server(config["remote_replay_socket"])
    else:
        threading.Thread(target=broker.start_local_replay_server).start()
