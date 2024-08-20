#!/bin/bash


echo "1. testnet 197"
echo "2. subtensor template testnet"
echo "3. sylliba subnet"
echo "4. subnet 19"
echo "5. choose submodule"


install_module() {
    module_name=$1
    module_url=$2
    module_path=$3
    if [ ! -d .$module_name ]; then
        python -m venv .$module_name
        source .$module_name/bin/activate
    else
        source .$module_name/bin/activate
    fi
    pip install -r requirements.txt
    
    if [ ! -d $module_path ]; then
        git clone $module_url module_validator/chain/$module_name
        pip install -e $module_path
    fi
}

install_submodule() {
    submodule_name=$1
    submodule_install_path=$2
    python -m module_validator.custom_modules --module_type $submodule_name --output $submodule_install_path
}

read -p "Select subnet or module to run[1]: " module

if [ $module == 1 ]; then
    module_name=sylliba
    module_url=https://github.com/agent-artificial/sylliba-subnet
    module_path=module_validator/chain/$module_name
    install_module $module_name $module_url $module_path

elif [ $module == 2 ]; then
    module_name=bittensor_subnet_template
    module_url=https://github.com/opentensor/bittensor-subnet-template
    module_path=module_validator/chain/$module_name
    install_module $module_name $module_url $module_path

elif [ $module == 3 ]; then
    module_name=sylliba
    module_url=https://github.com/agent-artificial/sylliba-subnet
    module_path=module_validator/chain/$module_name
    if [ ! -d .sylliba ]; then
        python -m venv .$module_name
    fi
    install_module $module_name $module_url $module_path
    pip install bittensor
    touch module_validator/chain/$module_name/__init__.py
    sed -i 's/template\/__init__.py/sylliba\/__init__.py/g' "module_validator/chain/sylliba/setup.py"
    submodule_name=translation
    submodule_install_path=$module_path/modules/$submodule_name
    install_submodule $submodule_name $submodule_install_path
    cd module_validator/chain/$module_name
    rm -r modules/translation
    ln -s /home/bakobi/vscode/module_validator/module_validator/modules/translation modules
    cd "../../.."

elif [ $module == 4 ]; then
    module_name=vision
    module_url=https://github.com/namoray/vision
    module_path=module_validator/chain/$module_name
    install_module $module_name $module_url $module_path
    python -m utils.add_environment_variables $module_path/config/config.py
    python -m utils.configuration.py 
    cp .env module_validator/chain/$module_name/.env


elif [ $module == 5 ]; then
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



