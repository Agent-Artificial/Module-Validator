#!/bin/bash

set -e

#export MODULE_VALIDATOR_ENV=production
export MODULE_VALIDATOR_ENV=development

create_environmnet() {
    module_name=$1
    source_file=.$module_name/bin/activate
    echo creating environment: $source_file

    if [ ! -d .$module_name ]; then
        python -m venv .$module_name
    fi
    source "$source_file"
    pip install --upgrade pip
    pip install setuptools wheel
    pip install -r requirements.txt
    echo "Environment created: $source_file"
}

# Installs the inference module from the module registrar API
install_inference_module() {
    submodule_name=$1
    python -m module_validator.custom_modules --module_type $submodule_name
}

# Prompt the use to selection from these options.
echo "1. sylliba"
echo "2. bittensor_subnet_template"
echo "3. vision"
echo "0. choose submodule"

# Ensure an option is selected
if [ -z $1 ]; then
    read -p "Select subnet or module to run[1]: " module
else 
    module=$1
fi

# Install sylliba subnet module
if [ $module == 1 ]; then
    # Declare variables
    module_name=sylliba
    module_url=https://github.com/agent-artificial/sylliba-subnet
    module_path=module_validator/subnet_modules/$module_name

    # check if the environment directory exists
    if [ ! -d .sylliba ]; then
        python -m venv .$module_name
    fi
    create_environmnet $module_name
    # install the translation module
    submodule_name=translation
    install_inference_module $submodule_name

    injected_command=sylliba_injected_command
    # install the repo locally to subnet_modules/sylliba
    echo "Install sylliba subnet module"

    bash_scripts/setup_sylliba.sh
    
    # confirm bittensor is installed
    pip install bittensor

    # declare variable
    submodule_name=translation


elif [ $module == 2 ]; then
    module_name=bittensor_subnet_template
    module_url=https://github.com/opentensor/bittensor-subnet-template
    module_path=module_validator/subnet_modules/$module_name
    install_module $module_name $module_url $module_path  


elif [ $module == 3 ]; then
    module_name=vision
    module_url=https://github.com/namoray/vision
    module_path=module_validator/subnet_modules/$module_name
    install_module $module_name $module_url $module_path
    python -m utils.add_environment_variables $module_path/config/config.py
    python -m utils.configuration.py 
    cp .env module_validator/subnet_modules/$module_name/.env


elif [ $module == 0 ]; then
    echo "1. translation"
    ehco "2. embedding"
    echo "3. financialnews"
    read -p "Select module to run[1]: " module

    if [ $module == 1 ]; then
        submodule_name=translation
    elif [ $module == 2 ]; then
        submodule_name=embedding
    elif [ $module == 3 ]; then
        submodule_name=financialnews
    fi
    submodule_install_path=module_validator/modules/$submodule_name
    install_submodule $submodule_name $submodule_install_path
fi


pip install -e .


echo "Remember to source your environment: source .$module_name/bin/activate"



