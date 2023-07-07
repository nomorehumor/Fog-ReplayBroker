#!/bin/env bash

ssh -i ../ssh_key.pem ubuntu@$(cat ip.txt)
