from datetime import datetime

TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def deserialize_timestamp(timestamp: str):
    return datetime.strptime(timestamp, TIME_FORMAT)

def serialize_msg(msg):
    serialized = {**msg}
    serialized["arrival_time"] = msg["arrival_time"].strftime(TIME_FORMAT)
    serialized["timestamp"] = msg["timestamp"].strftime(TIME_FORMAT)
    return serialized

def deserialize_msg(msg):
    deserialized = {**msg}
    deserialized["arrival_time"] = datetime.strptime(msg["arrival_time"], TIME_FORMAT)
    deserialized["timestamp"] = datetime.strptime(msg["timestamp"], TIME_FORMAT)
    return deserialized