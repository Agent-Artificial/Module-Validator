#!/bin/bash

set -e

# Clones and installs the subnet repo into module_validator/subnet_modules
install_subnet_module() {
    module_name=$1
    module_url=$2
    module_path=$3
    inject_command=$4
    if [ ! -d .$module_name ]; then
        python -m venv .$module_name
        source .$module_name/bin/activate
    else
        source .$module_name/bin/activate
    fi
    if [ ! -d $module_path ]; then
        git clone $module_url $module_path
    fi
    cd $module_path

    if [ ! -z $inject_command ]; then
        $inject_command
    fi

    pip install -e .
    pip install -r requirements.txt

}

# Installs the inference module from the module registrar API
install_inference_module() {
    submodule_name=$1
    python -m module_validator.custom_modules --module_type $submodule_name
}

sylliba_injected_command() {
    git switch sylliba
    # Create a init file so the repo can act as a package
    touch __init__.py
    # This is a work around for a bug in the subnet repo's code
    # TODO: Make this change in the subnet repo
    sed -i 's/template\/__init__.py/sylliba\/__init__.py/g' "setup.py"
    # Run the local setup script
    bash setup.sh
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

    injected_command=sylliba_injected_command
    # install the repo locally to subnet_modules/sylliba
    echo "Install sylliba subnet module"
    install_subnet_module $module_name $module_url $module_path $injected_command

    # confirm bittensor is installed
    pip install bittensor

    # declare variable
    submodule_name=translation

    # install the translation module
    install_inference_module $submodule_name

    # switch branches
    cd $module_path


    cd ../../../
    rm -r ${PWD}/module_validator/subnet_modules/sylliba/modules/translation
    ln -s ${PWD}/module_validator/modules/translation ${PWD}/module_validator/subnet_modules/sylliba/modules/translation
  

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



