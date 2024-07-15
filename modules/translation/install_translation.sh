#!/bin/bash

set -e

source ./.venv/bin/activate

python -m pip install --upgrade pip

pip install setuptools wheel gnureadline
pip install sndfile ggml-python substrate-interface communex loguru

sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install libsndfile1-dev -y

if [ ! -d "./modules/translation/seamless" ]; then
    git clone https://github.com/facebookresearch/seamless_communication.git ./modules/translation/seamless
    pip install ./modules/translation/seamless
fi

pip install ./modules/translation/seamless

pip install git+https://github.com/huggingface/transformers torch torchaudio torchvision fairseq2

mkdir -p ./modules/translation/in

mkdir -p ./modules/translation/out

