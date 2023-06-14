import zmq
import time
import threading

def request():
    # Create a context and socket for the client
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5560")

    # Send a message to the server
    socket.send_string("Hello from the client!")

    # Wait for a response from the server
    time.sleep(1)
    message = socket.recv_string()

    # Print the received message from the server
    print("Received message from server:", message, flush=True)


def respond():
    # Create a context and socket for the server
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5560")

    while True:
        # Receive a message from the client
        message = socket.recv_string()

        # Check if a message was received
        if message:
            # Print the received message from the client
            print("Received message from client:", message, flush=True)

            # Send a response back to the client
            socket.send_string("Hello from the server!")

        # Wait for a short period before checking for new messages
        time.sleep(1)


if __name__ == "__main__":
    # Start a separate thread for the server and client
    threading.Thread(target=respond).start()
    threading.Thread(target=request).start()
