#!/bin/bash

module_path=$1

if [ -z "$module_path" ]; then
    module_path=module_validator/subnet_modules/sylliba
fi

read -p "Would you like to configure your environment?(y/n): " CONFIG

if [ "$CONFIG" = "y" ]; then
    echo "Configuring"
    echo "Enter your network. finney, test, local"
    read -p "Enter your network: " BT_NETWORK
    read -p "Enter your subnet netuid: " BT_NETUID
    read -p "Enter your miner PORT: " BT_AXON_PORT
    read -p "Enter your miner IP: " BT_AXON_IP
    read -p "Enter your miner external PORT: "  BT_AXON_EXTERNAL_PORT
    read -p "Enter your miner external IP: " BT_AXON_EXTERNAL_IP
    read -p "Enter your miner max workers: " BT_AXON_MAX_WORERS
    read -p "Enter your miner coldkey: " BT_MINER_COLDKEY
    read -p "Enter your miner hotkey: " BT_MINER_HOTKEY
    read -p "Enter your validator coldkey: " BT_VALIDATOR_COLDKEY
    read -p "Enter your validator hotkey: " BT_VALIDATOR_HOTKEY
    read -p "Enter your wallet path: " BT_WALLET_PATH
    read -p "Enter your text_inference url: " INFERENCE_URL
    read -p "Enter your text_inference api key: " INFERENCE_API_KEY
fi
python utils/config_generator.py --file_dir $module_path
cat <<EOF >> .sylliba.env
BT_NETWORK="$BT_NETWORK"
BT_NETUID=$BT_NETUID
BT_AXON_PORT=$BT_AXON_PORT
BT_AXON_IP="$BT_AXON_IP"
BT_AXON_EXTERNAL_PORT=$BT_AXON_EXTERNAL_PORT
BT_AXON_EXTERNAL_IP="$BT_AXON_EXTERNAL_IP"
BT_AXON_MAX_WORERS=$BT_AXON_MAX_WORERS
BT_MINER_COLDKEY="$BT_MINER_COLDKEY"
BT_MINER_HOTKEY="$BT_MINER_HOTKEY"
BT_VALIDATOR_COLDKEY="$BT_VALIDATOR_COLDKEY"
BT_VALIDATOR_HOTKEY="$BT_VALIDATOR_HOTKEY"
BT_WALLET_PATH="$BT_WALLET_PATH"
INFERENCE_URL="$INFERENCE_URL"
INFERENCE_API_KEY="$INFERENCE_API_KEY"
EOF



