FROM ubuntu:latest
WORKDIR /usr/app/src

# Update package manager (apt-get) 
# and install (with the yes flag `-y`)
# Python and Pip
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip
COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY persistance.py ./
COPY broker.py ./
COPY replaybroker.py ./
COPY configs/ ./configs/

ENTRYPOINT ["python3", "-u", "replaybroker.py"]