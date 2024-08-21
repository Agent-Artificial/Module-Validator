#!/bin/bash

set -e

cd ..

source .sylliba/bin/activate

source .config_model.env

# Path to your .env file
env_file=$1

# Check if the .env file exists
if [[ ! -f "$env_file" ]]; then
  echo ".env file not found at $env_file"
  exit 1
fi

# Initialize an empty string for command line arguments
cmd_args=""

# Load the .env file and construct the command line arguments
while IFS='=' read -r key value; do
  # Ignore lines starting with '#' (comments) and empty lines
  if [[ ! "$key" =~ ^# && -n "$key" ]]; then
    # Trim whitespace from key and value
    key=$(echo $key | xargs)
    value=$(echo $value | xargs)

    # Add the key-value pair as a command line argument
    cmd_args+="--${key} ${value} "
  fi
done < "$env_file"
cp $env_file module_validator/chain/sylliba/.env

# Output the constructed command line arguments
echo "Constructed command line arguments: $cmd_args"

if not [ -d module_validator/chain/sylliba/modules/translation ]; then
    if not [ -d module_validator/chain/modules ]; then
        mkdir module_validator/chain/modules
        bash setup.sh translation
    fi

    if not [ -d module_validator/chain/sylliba/modules ]; then
        mkdir module_validator/chain/sylliba/modules
        ln -s ${PWD}/module_validator/modules/translation ${PWD}/module_validator/chain/sylliba/modules/translation
    fi
    if not [ -d module_validator/chain/sylliba/modules/translation ]; then
        ln -s ${PWD}/module_validator/modules/translation ${PWD}/module_validator/chain/sylliba/modules/translation
    else
        rm -r module_validator/chain/sylliba/modules/translation
        ln -s ${PWD}/module_validator/modules/translation ${PWD}/module_validator/chain/sylliba/modules/translation
    fi
fi

# Change directory to the sylliba module
cd module_validator/chain/sylliba

# Run the command

python -m neurons.validator $cmd_args