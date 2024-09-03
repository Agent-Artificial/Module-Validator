#!/bin/bash

subnet_name=$1
environment_path=.$subnet_name
config_path=module_validator/config/$subnet_name
submodule_path=module_validator/subnet_modules/$subnet_name

sudo rm -r $environment_path $config_path $submodule_path
