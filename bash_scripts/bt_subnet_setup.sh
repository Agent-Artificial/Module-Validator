#!/bin/bash

set -e

# Install $module_name subnet module

module_name=$1
root=${PWD}
module_path="$root/module_validator/subnet_modules/$module_name"

if [ -z "$module_path" ]; then
    module_path="$root/module_validator/subnet_modules/$module_name"
fi

# Activate the $module_name virtual environment
if [ ! -d "$root/.module_name" ]; then
    python -m venv "$root/.$module_name"
fi
source "$root/.$module_name/bin/activate"

# Clone the subnet repo
if [ ! -d "$module_path" ]; then
    git clone https://github.com/agent-artificial/$module_name-subnet "$module_path"
fi

# Switch to the subnet repo
cd "$module_path" || exit

# Create a init file so the repo can act as a package
touch __init__.py

# Switch to the $module_name branch
git switch "$module_name"


# Install dependencies
sudo apt-get update && sudo apt-get upgrade -y

sudo apt install -y make build-essential git clang curl libssl-dev llvm libudev-dev protobuf-compiler tmux libsndfile1-dev

pip install --upgrade pip

pip install setuptools wheel

pip install -r requirements.txt


# Install the $module_name subnet module
pip install -e .


# Switch back to the root
cd ../../..


# Setup the environment
bash "bash_scripts/$environment_module_name.sh" "$root/$module_path"
