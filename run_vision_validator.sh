#!/bin/bash

source .vision/bin/activate

cd module_validator/chain/vision

bash launch_validators.sh --env_file .env