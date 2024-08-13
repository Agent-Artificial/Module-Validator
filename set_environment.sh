#!/bin/bash


read -p "Select the environment (development/production): " environment

if [ "$environment" == "development" ]; then
    export MODULE_VALIDATOR_ENVIRONMENT=development
    if [ ! -d .venv ]; then
        python -m venv .venv
    fi
    source .venv/bin/activate
    read -p "Setup the virtual environment? (y/n): " setup_venv
    if [ "$setup_venv" == "y" ]; then
        pip install -r "module_validator/config/$environment/requirements.txt"
    fi
elif [ "$environment" == "production" ]; then
    source .venv/bin/activate
else
    echo "Invalid environment"
    exit 1
fi