#!/bin/bash

set -e

source ./.venv/bin/activate

python -m pip install --upgrade pip

pip install setuptools wheel gnureadline
pip install sndfile ggml-python substrate-interface bittensor loguru
pip install fastapi uvicorn loguru requests substrate-interface sentencepiece protobuf

if command -v apt-get >/dev/null; then
    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install python3 python3-dev python3-venv python3-pip python-is-python3 libsndfile1-dev libgmp10-dev -y
elif command -v pacman >/dev/null; then
    sudo pacman -Syu --noconfirm
    sudo pacman -S python python-pip python-virtualenv libsndfile gmp --noconfirm
else
    echo "This script requires a Linux distribution with either apt or pacman."
    exit 1
fi

if [ ! -d "./modules/translation/seamless" ]; then
    git clone https://github.com/facebookresearch/seamless_communication.git ./modules/translation/seamless
    
fi
pip install ./modules/translation/seamless
pip install git+https://github.com/huggingface/transformers torch torchaudio torchvision fairseq2

mkdir -p ./modules/translation/in

mkdir -p ./modules/translation/out
