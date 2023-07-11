# Reliable Message Delivery Prototype

The assignment repository for the "Fog Computing course (SS2023)" course at TU Berlin.

Authors:
- Alexander Guttenberger
- Maxim Popov

## Assignment Deliveries
The assignment deliveries can be found at root of the repository.
- Demo Video -> demo_presentation_video.mp4
- Documentation -> documentation.pdf

## Project Structure
The repository is organized as follows:
```
├── README.md                      # Documentation file for the repository
├── LICENSE                        # License file
├── demo_presentation_video.mp4    # Demo video of the working solution
├── documentation.pdf              # Documentation of the solution
├── deploy                         # Folder containing deployment files
│   ├── firewall.tf                # Terraform configuration for the firewall
│   ├── output.tf                  # Terraform configuration for output variables
│   ├── provider.tf                # Terraform configuration for the provider
│   ├── setup.sh                   # Shell script for setup
│   ├── ssh_into_vm.sh             # Shell script for SSH into VM
│   ├── ssh_key.tf                 # Terraform configuration for SSH key
│   └── vm.tf                      # Terraform configuration for virtual machine
├── docker-compose.cloud.yml       # Docker Compose configuration for cloud environment
├── prototyping_assignment.pdf     # PDF file for prototyping assignment
├── requirements.txt               # File listing the required Python packages
└── src                            # Source code folder
    ├── cloud_components.py        # Python file for cloud components
    ├── fog_components.py          # Python file for fog components
    ├── replay_broker              # Folder for replay broker
    │   ├── Dockerfile             # Dockerfile for replay broker
    │   ├── __init__.py            # Initialization file for replay broker
    │   ├── broker.py              # Python file for broker
    │   ├── configs                # Folder containing configuration files
    │   │   ├── broker.yaml        # YAML configuration file for broker
    │   │   ├── cloud_broker.yaml  # YAML configuration file for cloud broker
    │   │   └── fog_broker.yaml    # YAML configuration file for fog broker
    │   ├── logging_formatter.py   # Python file for logging formatter
    │   ├── persistance.py         # Python file for persistence
    │   ├── replaybroker.py        # Python file for replay broker
    │   ├── requirements.txt       # File listing the required Python packages for replay broker
    │   ├── serialization.py       # Python file for serialization
    │   ├── start_brokers.py       # Python file for starting brokers
    │   ├── start_cloud.py         # Python file for starting cloud
    │   └── start_fog.py           # Python file for starting fog
    ├── sensor                     # Folder for sensor
    │   ├── Dockerfile             # Dockerfile for sensor
    │   ├── configs                # Folder containing configuration files
    │   │   ├── sensor_cloud.yaml  # YAML configuration file for sensor in cloud
    │   │   └── sensor_fog.yaml    # YAML configuration file for sensor in fog
    │   ├── requirements.txt       # File listing the required Python packages for sensor
    │   └── sensor.py              # Python file for sensor
    └── subscriber                 # Folder for subscriber
        ├── configs                # Folder containing configuration files
        │   └── subscriber.yaml    # YAML configuration file for subscriber
        ├── requirements.txt       # File listing the required Python packages for subscriber
        └── subscriber.py          # Python file for subscriber
```

## Testing nodes locally only
To execute the test scenario you should follow these steps:
1. Install requirements: `pip install -r requirements.txt`
2. Install and run MongoDB
3. Run fog components by executing: `python3 src/fog_components.py`
4. Run cloud components: `python3 src/cloud_components.py`

## Deployment

### Prerequisites
Before deploying the application, ensure you have the following:

- [Terraform](https://www.terraform.io/downloads.html) installed on your system.
- A Tailscale account created and Tailscale [installed](https://tailscale.com/download) on your local machine.
- The Google Cloud Platform (GCP) service account key downloaded from [GCP](https://console.cloud.google.com/iam-admin/serviceaccounts/details/117466062831806713474/keys?project=fog-computing-391310). Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the downloaded key, for example: `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key.json`.

### Deploying on GCP

1. Change to the deployment directory: `cd deploy`.
2. Initialize the Terraform environment: `terraform init`.
3. Apply the infrastructure using Terraform: `terraform apply`.
4. SSH into the VM instance using the command: `ssh -i ssh_key.pem ubuntu@vm_ip`. Replace `vm_ip` with the IP address of the VM (you can find the IP address in `ip.txt`).

#### Installing Tailscale for NAT traversal

5. Install Tailscale by running the command: `curl -fsSL https://tailscale.com/install.sh | sh`, and log in to your Tailscale account.
6. Start Tailscale by running: `sudo tailscale up`.

#### Running the Cloud Node

7. Install the required Python packages: `pip install -r requirements.txt`.
8. Change the remote server address in the `src/replay_broker/cloud_config.yml` file to the Tailscale IP address of your fog node.
9. Run the Cloud Node application: `python3 src/cloud_components.py`.

#### Shutdown

10. Exit the application and the SSH connection.
11. To clean up and destroy the infrastructure created by Terraform, run: `terraform destroy`.

### Deploying the Fog Node on a Local Machine

1. Update the remote server address in the `src/replay_broker/fog_config.yml` file to the Tailscale IP address of your cloud node. For example, change `remote_replay_socket: "tcp://127.0.0.1:4411"` to `remote_replay_socket: "tcp://35.246.212.91:4411"`.
2. Start MongoDB with docker: `docker run --name mongodb -d -p 27017:27017 mongo:latest`
3. Install the required Python packages: `pip install -r requirements.txt`.
4. Run the Fog Node application: `python3 src/fog_components.py`.
