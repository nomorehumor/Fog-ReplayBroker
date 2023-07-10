#!/bin/bash

# This script is used to push changes to the VM.
ssh -i ssh_key.pem ubuntu@$(cat ip.txt) "rm -rf /home/ubuntu/src"
scp -i ssh_key.pem -r ../src ubuntu@$(cat ip.txt):/home/ubuntu