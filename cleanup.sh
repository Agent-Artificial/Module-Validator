#!/bin/bash

subnet_name=$1
environment_path=.$subnet_name
config_path=module_validator/config/$subnet_name
submodule_path=module_validator/subnet_modules/$subnet_name
dotenv_path=$environment_path.env

if [ -z "$subnet_name" ]; then
    echo "Usage: cleanup.sh <subnet_name>"
    exit 1
fi
sudo rm -r $environment_path $config_path $submodule_path $dotenv_path
