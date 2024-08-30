#!/bin/bash

set -e

FILE_PATH=$1
if [ -z "$FILE_PATH" ]; then
    read -p "Enter file path: " FILE_PATH
fi
if [ -f "$FILE_PATH" ]; then
    echo "Invalid file path"
    read -p "Enter file path: " FILE_PATH
    python -m utils.config_generator $FILE_PATH
fi

python -m utils.config_generator $FILE_PATH

