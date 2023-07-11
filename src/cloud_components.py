import os
from replay_broker.replaybroker import ReplayBroker
from sensor.sensor import Sensor, DATA_WEATHER
import threading
import yaml

if __name__ == "__main__":

    with open(os.path.dirname(os.path.realpath(__file__)) + "/replay_broker/configs/cloud_broker.yaml", "r") as f:
        cloud_config = yaml.safe_load(f)

    # Start cloud broker
    cloudBroker = ReplayBroker(
        sub_socket=cloud_config["sub_socket"],
        pub_socket=cloud_config["pub_socket"],
        db_url=cloud_config["db_url"],
        queue_size=cloud_config["queue_size"],
        replay_socket=cloud_config["replay_socket"],
        remote_data_name=cloud_config["remote_data_name"]
    )

    threading.Thread(target=cloudBroker.start_local_replay_server).start()

    # Start sensor
    with open(os.path.dirname(os.path.realpath(__file__)) + "/sensor/configs/sensor_cloud.yaml", "r") as s:
        sensor_config = yaml.safe_load(s)

    # Weather sensor (or API simulation)
    sensor = Sensor(socket_address=sensor_config["socket"], delay=sensor_config["delay"])
    threading.Thread(target=sensor.start, args=(DATA_WEATHER,)).start()
