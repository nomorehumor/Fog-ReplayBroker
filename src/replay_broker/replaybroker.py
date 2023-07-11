import argparse
from broker import Broker
import time
import threading
import zmq
import os
import yaml
import logging
from serialization import serialize_msg, deserialize_msg, deserialize_timestamp
from logging_formatter import CustomFormatter

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

REQUEST_INTERVAL = 2
REQUEST_TIMEOUT = 5

class ReplayBroker(Broker):
    def __init__(self, sub_socket: str, pub_socket: str, db_url: str, queue_size: int, replay_socket: str, remote_data_name: str) -> None:
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
        self.last_event_date = self.repository.find_latest_data(remote_data_name)
        self.remote_data_name = remote_data_name
        # The address for the remote replay socket.
        self.remote_replay_server_socket = None
        self.request_in_progress = False
        self.send_replay_lock = threading.Lock()
        self.first_event_date = None
        
        self.data_poll_thread = threading.Thread(target=self.poll)
        self.data_poll_thread.start()

    def connect_to_remote_replay_server(self, remote_replay_address):
        """
        Connects to the remote replay server.
        """
        self.remote_replay_address = remote_replay_address

    def start_local_replay_server(self):
        """
        Receives replay requests from the client and sends the requested events.
        """
        logging.info("SERVER: Starting local replay server...")
        while True:

            # Receive a message from the client
            request = self.local_replay_socket.recv_json()
            logging.info(f"SERVER: Got replay request {request}")
            if request:
                request_type = request.get("type")

                if request_type == "replay_by_timestamp":
                    last_event_date = deserialize_msg(request.get("last_event_date"))
                    events = self.repository.find_data_after_arrival_time(last_event_date["arrival_time"], request.get("data_name"))
                elif request_type == "replay_all":
                    events = self.repository.get_data_all(request.get("data_name"))

                events_serialized = [serialize_msg(event) for event in events ]
                self.local_replay_socket.send_json(events_serialized)

            # Wait for a short period before checking for new messages
            time.sleep(1)

    def start_replay_request_loop(self):
        while True:
            if not self.request_in_progress:  # Only send a new request if one is not already in progress
                self.send_replay_request(REQUEST_TIMEOUT)
            time.sleep(REQUEST_INTERVAL)

    def send_replay_request(self, timeout):
        if self.last_event_date is None:
            request = {"type": "replay_all", "data_name": self.remote_data_name}
        else:
            request = {
                "type": "replay_by_timestamp", 
                "data_name": self.remote_data_name,
                "last_event_date": serialize_msg(self.last_event_date)
                }

        with self.send_replay_lock:
            self.request_in_progress = True  # Set the flag to indicate that a request is in progress
            threading.Thread(target=self._send_replay_request, args=(request, timeout)).start()

    def _send_replay_request(self, request, timeout):
        try:
            # Create connection to remote replay server
            self.remote_replay_server_socket = self.context.socket(zmq.REQ)
            self.remote_replay_server_socket.setsockopt(zmq.CONNECT_TIMEOUT, timeout * 1000)
            self.remote_replay_server_socket.setsockopt(zmq.RCVTIMEO, timeout * 1000)
            self.remote_replay_server_socket.connect(self.remote_replay_address)

            # Send the replay request to the remote replay server
            logging.info(f"CLIENT: Sending replay request '{request.get('type')}' to {self.remote_replay_address}")
            self.remote_replay_server_socket.send_json(request)
            response = self.remote_replay_server_socket.recv_json()
            self.handle_replay_events(response)
        except zmq.error.Again:
            logging.warning(f"CLIENT: Resource temporarily unavailable. Retrying in {REQUEST_INTERVAL} sec...")
            time.sleep(REQUEST_INTERVAL)
            # Handle the temporary unavailability, such as adding a delay and retrying later
        finally:
            self.remote_replay_server_socket.close()
            self.request_in_progress = False

    def process_replay_msg(self, msg):
        msg_deserialized = deserialize_msg(msg)
        self.repository.insert_value(msg_deserialized, msg_deserialized["name"])

    def handle_replay_events(self, events):
        logging.debug(f"CLIENT: Received {len(events)} replay events: {events}")
        if events is None:
            return
         
        for event in events:
            self.process_replay_msg(event)
            self.last_event_date = self.repository.find_latest_data(self.remote_data_name)


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
        replay_socket=config["replay_socket"],
        remote_data_name=config["remote_data_name"]
    )
    if args.replay:
        broker.connect_to_remote_replay_server(config["remote_replay_socket"])
        threading.Thread(target=broker.start_replay_request_loop).start()
    threading.Thread(target=broker.start_local_replay_server).start()
