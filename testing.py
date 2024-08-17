import json
import argparse
import os
import subprocess
import argparse
import bittensor as bt
from dotenv import load_dotenv
from loguru import logger
from typing import List, Optional, Dict, Any
from typing_extensions import Self
from bittensor.axon import FastAPIThreadedServer
from utils.create_bittensor_config import main as config_main, StreamPrompting, cli
from module_validator.chain.bittensor_subnet_template.docs.stream_tutorial.miner import StreamMiner, StreamPrompting
from module_validator.chain.bittensor_subnet_template.docs.stream_tutorial.config import get_config, check_config
fro

load_dotenv()


class AddConfigs:
    def __init__(self):
        cli()
        self.command = self.add_args()
        print(self.command)
        self.args = subprocess.run(self.command, capture_output=True, text=True)
        
        

        

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "Hi how are you?"
    },
    {
        "role": "assistant",
        "content": "I am doing well! How can I assist you?"
    },
    {
        "role": "user",
        "content": "can you write me a short paragraph about Bitcoin?"
    }
]

add_args = AddConfigs()

configs = get_config()
print(configs)

class Miner(StreamMiner):
    def __init__(self, configs):
        super().__init__(configs)
        self.config = self.config(configs)
        
    def config(self, config) -> "bt.Config":
        return check_config(self.config, config)
        
    
    def prompt(self, *args, **kwargs):
        return self.config.prompt(*args, **kwargs)
    
    def add_args(self, *args, **kwargs):
        return add_args(*args, **kwargs)
    

miner = Miner(configs)
