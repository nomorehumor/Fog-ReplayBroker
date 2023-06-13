import zmq
import time
import threading

# Broker function to proxy communication between client and server
def broker():
    context = zmq.Context()
    backend = context.socket(zmq.XSUB)  # XSUB socket for receiving messages from multiple publishers
    backend.bind("tcp://*:5560")  # Bind frontend socket to port 5559
    frontend = context.socket(zmq.XPUB)  # XPUB socket for distributing messages to multiple subscribers
    frontend.bind("tcp://*:5559")  # Bind backend socket to port 5560

    zmq.proxy(frontend, backend)  # Proxy messages from frontend to backend

# Server function to publish messages
def publisher():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)  # PUB socket for publishing messages
    publisher.connect("tcp://127.0.0.1:5560")  # Connect socket to backend of the broker

    i = 0
    while True:
        message = f"Hello from the publisher! {i}"
        i += 1
        publisher.send_string(message)  # Send message to subscribers
        time.sleep(1)

# Client function to subscribe and receive messages
def subscribe():
    context = zmq.Context()
    subscribe = context.socket(zmq.SUB)  # SUB socket for subscribing to messages
    subscribe.connect("tcp://127.0.0.1:5559")  # Connect socket to frontend of the broker
    subscribe.setsockopt(zmq.SUBSCRIBE, b'')  # Subscribe to all messages

    while True:
        message = subscribe.recv_multipart()
        print(message)

# Start the broker, publisher, and client threads
if __name__ == "__main__":
    threading.Thread(target=publisher).start()
    threading.Thread(target=broker).start()
    time.sleep(4)
    threading.Thread(target=subscribe).start()
