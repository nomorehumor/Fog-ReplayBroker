import os
from replay_broker.replaybroker import ReplayBroker
from sensor.sensor import DataProvider
import threading
import yaml

if __name__ == "__main__":

    with open(os.path.dirname(os.path.realpath(__file__)) + "/replay_broker/configs/cloud_broker.yaml", "r") as f:
        cloud_config = yaml.safe_load(f)

    ## start cloud server
    cloudBroker = ReplayBroker(
        sub_socket=cloud_config["sub_socket"],
        pub_socket=cloud_config["pub_socket"],
        db_url=cloud_config["db_url"],
        queue_size=cloud_config["queue_size"],
        replay_socket=cloud_config["replay_socket"],
        remote_data_name=cloud_config["remote_data_name"]
    )

    # connect to remote replay server
    cloudBroker.connect_to_remote_replay_server(cloud_config["remote_replay_socket"])
    threading.Thread(target=cloudBroker.start_replay_request_loop).start()

    # start cloud server
    threading.Thread(target=cloudBroker.start_local_replay_server).start()

    ## start sensor
    with open(os.path.dirname(os.path.realpath(__file__)) + "/sensor/configs/sensor.yaml", "r") as s:
        sensor_config = yaml.safe_load(s)

    sensor = DataProvider(socket_address=sensor_config["socket"], delay=sensor_config["delay"])
    threading.Thread(target=sensor.start, args=('weather',)).start()
