#!/bin/bash

set -e

source ./.venv/bin/activate
source .env

MINER_NAME="$1"
KEYPATH_NAME="$2"
MINER_HOST="$3"
MINER_PORT="$4"
STAKE="$5"
NETUID="$6"
FUNDING_KEY="$7"
MODIFIER=$8

if [ -z "$MINER_NAME" ]; then
    read -p "Enter miner name: " MINER_NAME
fi
if [ -z "$KEYPATH_NAME" ]; then
    read -P "Enter keyfile name: " KEYPATH_NAME
fi
if [ -z "$MINER_HOST" ]; then
    read -p "Enter miner host: " MINER_HOST
fi
if [ -z "$MINER_PORT" ]; then
    read -p "Enter miner port: " MINER_PORT
fi
if [ -z "$STAKE" ]; then
    read -p "Enter miner stake: " STAKE
fi
if [ -z "$NETUID" ]; then
    read -p "Enter netuid: " NETUID
fi
if [ ! -f "$KEY_PATH/$KEYPATH_NAME" ]; then
    echo "Creating key"
    comx key create "$KEYPATH_NAME"
fi
if [ -z "$FUNDING_KEY" ]; then
    read -p "Funding key? [keypath_name] " FUNDING_KEY
fi

read -p "Fund key? Stake amount $STAKE + $MODIFIER = $(($STAKE + $MODIFIER)) [y/n] " -n 1 -r
if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    
    comx balance transfer "$FUNDING_KEY" "$STAKE" "$MINER_NAME"
fi

read -p "Register miner? [y/n] " -n 1 -r
if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    comx register "$MINER_NAME" "$KEYPATH_NAME" --host "$MINER_HOST" --port "$MINER_PORT" --stake "$STAKE" --netuid "$NETUID"
fi
