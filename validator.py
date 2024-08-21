import json
import argparse
import bittensor as bt
from getpass import getpass
from substrateinterface import Keypair
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config_model import Config
from bittensor.axon import FastAPIThreadedServer
from pathlib import Path


def set_working_directory_to_submodule(submodule_path):
    # Get the full path of the current script (which should be in the project root)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the submodule
    submodule_full_path = os.path.join(project_root, submodule_path)
    
    # Verify that the submodule path exists
    if not os.path.exists(submodule_full_path):
        raise FileNotFoundError(f"Submodule path not found: {submodule_full_path}")
    
    # Change the current working directory
    os.chdir(submodule_full_path)
    
    # Add the submodule directory to sys.path to allow imports
    if submodule_full_path not in sys.path:
        sys.path.insert(0, submodule_full_path)
    
    print(f"Working directory set to: {os.getcwd()}")

set_working_directory_to_submodule("module_validator/chain/bittensor_subnet_template")

from neurons.validator import Validator as ExampleValidator


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    

class Validator(ExampleValidator):
    config = None
    subtensor = None
    wallet = None
    axon = None
    metagraph = None
    server_config = None
    fast_server = None
    
    def __init__(self, config):
        super().__init__(config)
        self.server_config = uvicorn.Config(app=app, host=os.getenv("axon_ip"), port=os.getenv("axon_port"))
        self.fast_server = FastAPIThreadedServer(config=self.server_config)
        self.config.fast_server = self.fast_server
        self.config = config
        self.subtensor = bt.subtensor(netowrk=self.config.subtensor.network, config=self.config, _mock=False, log_verbose=True)
        self.config.subtensor.config = self.config
        self.wallet = bt.wallet(name=self.config.wallet.name, hotkey=self.config.wallet.hotkey, path=self.config.wallet.path, config=self.config)
        self.config.wallet.config = self.config
        self.axon=bt.axon(wallet=self.wallet, config=self.config, port=self.config.axon.port, ip=self.config.axon.ip, external_ip=self.config.axon.external_ip, external_port=self.config.axon.external_port, max_workers=self.config.axon.max_workers)
        self.config.axon.config = self.config
        self.metagraph = bt.metagraph(netuid=self.config.netuid, network=self.config.subtensor.network, lite=True, sync=True)
        self.config.metagraph.config = self.config
        self.config = self.config
        

    
    def resync_metagraph(self):
        """Resyncs the metagraph and updates the hotkeys and moving averages based on the new metagraph."""
        self.metagraph.sync(subtensor=self.subtensor)

validator = Validator(Config())
print(validator.config)




# 
# validator.metagraph = metagraph
# 
# 
# validator.run()

