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

7. Install the required Python packages: `pip install -r src/requirements.txt`.
8. Change the remote server address in the `src/replay_broker/cloud_config.yml` file to the Tailscale IP address of your fog node.
9. Run the Cloud Node application: `python3 src/cloud_components.py`.

#### Shutdown

10. Exit the application and the SSH connection.
11. To clean up and destroy the infrastructure created by Terraform, run: `terraform destroy`.

### Deploying the Fog Node on a Local Machine

1. Update the remote server address in the `src/replay_broker/fog_config.yml` file to the Tailscale IP address of your cloud node. For example, change `remote_replay_socket: "tcp://127.0.0.1:4411"` to `remote_replay_socket: "tcp://35.246.212.91:4411"`.
2. Start MongoDB with docker: `docker run --name mongodb -d -p 27017:27017 mongo:latest`
3. Install the required Python packages: `pip install -r src/requirements.txt`.
4. Run the Fog Node application: `python3 src/fog_components.py`.
