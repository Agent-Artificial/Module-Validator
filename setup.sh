#!/bin/bash


echo "1. testnet 197"
echo "2. subtensor template testnet"
echo "3. syliba subnet"
echo "4. subnet 19"
echo "5. choose submodule"


read -p "Select subnet or module to run[1]: " module

if [ $module == 1 ]; then
    if [ ! -d .syliba ]; then
        python -m venv .syliba
    fi
    source .syliba/bin/activate
    pip install -r requirements.txt
    git clone https://bakobiibizo/vision module_validator/chain
    module_path=module_validator/chain/vision
    pip install -e $module_path
elif [ $module == 2 ]; then
    if [ ! -d .subtensor ]; then
        python -m venv .subtensor
    fi
    source .bittensor/bin/activate
    pip install -r requirements.txt
    git clone https://github.com/opentensor/bittensor-subnet-template module_validator/chain/bittensor_subnet_template
    module_path=module_validator/chain/bittensor_subnet_template
    pip install -e $module_path
elif [ $module == 3 ]; then
    if [ ! -d .syliba ]; then
        python -m venv .syliba
    fi
    source .syliba/bin/activate
    pip install -r requirements.txt
    git clone https://bakobiibizo/vision module_validator/chain
    module_path=module_validator/chain/bittensor_subnet
    pip install -e $module_path
elif [ $module == 4 ]; then
    if [ ! -d .subnet19 ]; then
        python -m venv .subnet19
    fi
    source .subnet19/bin/activate
    git clone https://github.com/namoray/vision module_validator/chain/subnet19
    pip install -r requirements.txt
    module_path=module_validator/chain/vision
    pip install -e $module_path
else
    if [ ! -d .custom_modules ]; then
        python -m venv .custom_modules
    fi
    source .custom_modules/bin/activate
    pip install -r requirements.txt
    python -m module_validator.custom_modules
fi

pip install -e .



