import zmq
import time
import threading

# Broker function to intercept and modify messages before forwarding
def broker():
    xpub_addr = 'tcp://127.0.0.1:5559'
    xsub_addr = 'tcp://127.0.0.1:5560'
    context = zmq.Context()

    #create XPUB 
    xpub_socket = context.socket(zmq.XPUB)
    xpub_socket.bind(xpub_addr)
    #create XSUB
    xsub_socket = context.socket(zmq.XSUB)
    xsub_socket.bind(xsub_addr)


    #create poller
    poller = zmq.Poller()
    poller.register(xpub_socket, zmq.POLLIN)
    poller.register(xsub_socket, zmq.POLLIN)


    while True:
        # get event
        event = dict(poller.poll())
        if xpub_socket in event:
            message = xpub_socket.recv_multipart()
            modified_message = modify_message(message)
            xsub_socket.send_multipart(modified_message)
        if xsub_socket in event:
            message = xsub_socket.recv_multipart()
            modified_message = modify_message(message)
            xpub_socket.send_multipart(modified_message)

# Function to modify the message (example: add a timestamp)
def modify_message(message):
    # Example modification: Add a timestamp to the message
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).encode()
    modified_message = [timestamp] + message  # Prepend the timestamp to the message

    return modified_message

# Publisher function to publish messages
def publisher():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)  # PUB socket for publishing messages
    publisher.connect("tcp://127.0.0.1:5560")  # Connect socket to backend of the broker

    while True:
        message = "Hello from the publisher!"
        publisher.send_string(message)  # Send message to subscribers
        time.sleep(1)

# Subscriber function to subscribe and receive messages
def subscriber():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)  # SUB socket for subscribing to messages
    subscriber.connect("tcp://127.0.0.1:5559")  # Connect socket to frontend of the broker
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')  # Subscribe to all messages

    while True:
        message = subscriber.recv_string()  # Receive message from publisher
        print("Received message from broker:", message)

# Start the broker, publisher, and subscriber threads
if __name__ == "__main__":
    threading.Thread(target=broker).start()
    threading.Thread(target=publisher).start()
    threading.Thread(target=subscriber).start()
