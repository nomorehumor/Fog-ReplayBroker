#!/bin/env bash

ssh-keygen -f "/home/alex/.ssh/known_hosts" -R $(cat ip.txt)
ssh -i ssh_key.pem ubuntu@$(cat ip.txt)
