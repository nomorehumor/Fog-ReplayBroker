## Deployment Cloud node on GCP

### prepare
1. To deploy the complete application with terraform follow these steps ([Install Terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform)):

2. Download the key to your system (be aware to not commit it) from [GCP](https://console.cloud.google.com/iam-admin/serviceaccounts/details/117466062831806713474/keys?project=fog-computing-391310)
3. Set the environment variable `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key.json`
4. Change to deploy directory with `cd deploy`
5. Setup your terraform environment with `terraform init`

### deploy and start the app
6. Apply the infrastructure with `terraform apply`
7. To ssh into the vm use "ssh -i ssh_key.pem ubuntu@vm_ip", change vm_ip with the ip of the vm (ip address can be also found in ip.txt)
8. run "pip install -r src/requirements.txt"
9. run "python3 src/cloud_components.py"

### shutdown
10. exit the app and the ssh connection
11. Shutdown with `terraform destroy`

## Deployment Fog node on local machine

1. change fog config remote server address in the `src/replay_broker/fog_config.yml` to the cloud vm ip e.g. from `remote_replay_socket: "tcp://127.0.0.1:4411"` to `remote_replay_socket: "tcp://35.246.212.91:4411"`
1. run "pip install -r src/requirements.txt"
2. run "python3 src/fog_components.py"
