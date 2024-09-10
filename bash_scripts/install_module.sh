#!/bin/bash

set -e

# Install sylliba subnet module
module_name=$1
module_path=$2
module_url=$3
root=${PWD}

if [ -z "$module_path" ]; then
    module_path=$root/module_validator/subnet_modules/$module_name
fi

# Activate the sylliba virtual environment
if [ ! -d "$root/.sylliba" ]; then
    python -m venv "$root/.sylliba"
fi
source "$root/.$module_name/bin/activate"
pip install -r requirements.txt
# Clone the subnet repo
if [ ! -d "$module_path" ]; then
    git clone "$module_url" "$module_path"
fi

# Switch to the subnet repo
cd "$module_path" || exit

# Create a init file so the repo can act as a package
touch __init__.py

pip install -e .

echo "$module_name installed" 

cd ../../..