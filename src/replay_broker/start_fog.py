import os
from replaybroker import ReplayBroker
import threading
import yaml

if __name__ == "__main__":
    with open(os.path.dirname(os.path.realpath(__file__)) + "/configs/fog_broker.yaml", "r") as f:
        fog_config = yaml.safe_load(f)

    with open(os.path.dirname(os.path.realpath(__file__)) + "/configs/cloud_broker.yaml", "r") as f:
        cloud_config = yaml.safe_load(f)

    fogBroker = ReplayBroker(
        sub_socket=fog_config["sub_socket"],
        pub_socket=fog_config["pub_socket"],
        db_url=fog_config["db_url"],
        queue_size=fog_config["queue_size"],
        replay_socket=fog_config["replay_socket"]
    )

    fogBroker.connect_to_remote_replay_server(fog_config["remote_replay_socket"])

    threading.Thread(target=fogBroker.start_replay_request_loop).start()