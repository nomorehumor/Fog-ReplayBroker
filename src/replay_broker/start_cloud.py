import os
from replaybroker import ReplayBroker
import threading
import yaml

if __name__ == "__main__":

    with open(os.path.dirname(os.path.realpath(__file__)) + "/configs/cloud_broker.yaml", "r") as f:
        cloud_config = yaml.safe_load(f)

    cloudBroker = ReplayBroker(
        sub_socket=cloud_config["sub_socket"],
        pub_socket=cloud_config["pub_socket"],
        db_url=cloud_config["db_url"],
        queue_size=cloud_config["queue_size"],
        replay_socket=cloud_config["replay_socket"],
        remote_data_name=cloud_config["remote_data_name"]
    )

    threading.Thread(target=cloudBroker.start_local_replay_server).start()