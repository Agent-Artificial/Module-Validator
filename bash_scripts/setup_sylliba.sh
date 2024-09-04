#!/bin/bash

set -e

# Install sylliba subnet module

module_path=$1
root=${PWD}

if [ -z "$module_path" ]; then
    module_path=$root/module_validator/subnet_modules/sylliba
fi

# Activate the sylliba virtual environment
if [ ! -d "$root/.sylliba" ]; then
    python -m venv "$root/.sylliba"
fi
source "$root/.sylliba/bin/activate"

# Clone the subnet repo
if [ ! -d "$module_path" ]; then
    git clone https://github.com/agent-artificial/sylliba-subnet "$module_path"
fi

# Switch to the subnet repo
cd "$module_path" || exit

# Create a init file so the repo can act as a package
touch __init__.py

# Switch to the sylliba branch
git switch sylliba

# This is a work around for a bug in the subnet repo's code
# TODO: Make this change in the subnet repo
sed -i 's/template\/__init__.py/sylliba\/__init__.py/g' "setup.py"

# Install dependencies
sudo apt-get update && sudo apt-get upgrade -y

sudo apt install -y make build-essential git clang curl libssl-dev llvm libudev-dev protobuf-compiler tmux libsndfile1-dev

pip install --upgrade pip

pip install setuptools wheel

pip install -r requirements.txt


# Install the sylliba subnet module
pip install -e .


# Switch back to the root
cd ../../..

# Symlink the translation module
rm -r ${PWD}/module_validator/subnet_modules/sylliba/modules/translation
ln -s ${PWD}/module_validator/modules/translation ${PWD}/module_validator/subnet_modules/sylliba/modules/translation

# Setup the environment
bash bash_scripts/environment_sylliba.sh "$root/$module_path"
