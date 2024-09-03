#!/bin/bash

set -e

# Define the directory to loop throug

DIRECTORY="module_validator/subnet_modules"

# Initialize an array to store folder names
folder_names=()

install_path=$1

if [[ -z "$install_path" ]]; then
  # Loop through the directory and collect folder names
  for folder in "$DIRECTORY"/*/; do
    # Get the base name of the folder
    folder_name=$(basename "$folder")
    # Add the folder name to the array
    folder_names+=("$folder_name")
  done

  # Check if there are any folders found
  if [[ ${#folder_names[@]} -eq 0 ]]; then
    echo "No folders found in $DIRECTORY."
    exit 1
  fi

  # Prompt the user to select a folder
  echo "Please select a folder from the list:"
  select folder_choice in "${folder_names[@]}"; do
    if [[ -n "$folder_choice" ]]; then
      echo "You selected: $folder_choice"
      break
    else
      echo "Invalid selection. Please try again."
    fi
  done
else 
  folder_choice=$install_path
fi
python -m utils.config_generator --file "$DIRECTORY/$folder_choice"