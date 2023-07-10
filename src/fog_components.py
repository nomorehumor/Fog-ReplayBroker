import os
from replay_broker.replaybroker import ReplayBroker
from sensor.sensor import DataProvider
import threading
import yaml

if __name__ == "__main__":

    with open(os.path.dirname(os.path.realpath(__file__)) + "/replay_broker/configs/fog_broker.yaml", "r") as f:
        fog_config = yaml.safe_load(f)

    ## start fog client
    fogBroker = ReplayBroker(
        sub_socket=fog_config["sub_socket"],
        pub_socket=fog_config["pub_socket"],
        db_url=fog_config["db_url"],
        queue_size=fog_config["queue_size"],
        replay_socket=fog_config["replay_socket"],
        remote_data_name=fog_config["remote_data_name"]
    )

    # connect to remote replay server
    fogBroker.connect_to_remote_replay_server(fog_config["remote_replay_socket"])
    threading.Thread(target=fogBroker.start_replay_request_loop).start()

    # start fog server
    threading.Thread(target=fogBroker.start_local_replay_server).start()

    # start sensor
    with open(os.path.dirname(os.path.realpath(__file__)) + "/sensor/configs/sensor.yaml", "r") as s:
        sensor_config = yaml.safe_load(s)

    sensor = DataProvider(socket_address=sensor_config["socket"], delay=sensor_config["delay"])
    threading.Thread(target=sensor.start, args=('energy_usage',)).start()