## Deployment on GCP
1. To deploy the complete application with terraform follow these steps ([Install Terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform)):

2. Download the key to your system (be aware to not commit it) from [GCP](https://console.cloud.google.com/iam-admin/serviceaccounts/details/117466062831806713474/keys?project=fog-computing-391310)
3. Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key.json`
4. Change to deploy directory with `cd deploy`
5. Setup your terraform environment with `terraform init`
6. Apply the infrastructure with `terraform apply`
7. To ssh into the vm use "ssh -i ssh_key.pem ubuntu@vm_ip", change vm_ip with the ip of the vm
8. Shutdown with `terraform destroy`
