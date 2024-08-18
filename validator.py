import json
import bittensor as bt
from getpass import getpass
from substrateinterface import Keypair
import os
import sys
from utils.configuration import main as config_main

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

from module_validator.chain.bittensor_subnet_template.neurons.validator import Validator as ExampleValidator


class Validator(ExampleValidator):
    config = None
    subtensor = None
    wallet = None
    axon = None
    metagraph = None
    
    def __init__(self, config, subtensor, wallet, axon, metagraph):
        super().__init__(config=config)
        self.config = config
        self.subtensor = subtensor
        self.wallet = wallet
        self.axon = axon
        self.metagraph = metagraph
    
    def resync_metagraph(self):
        """Resyncs the metagraph and updates the hotkeys and moving averages based on the new metagraph."""
        self.metagraph.sync(subtensor=self.subtensor)

    
    
config = config_main()
print(config)       
config.neuron.full_path = config.miner.full_path
subtensor = bt.Subtensor(config.subtensor.network, config=config)
wallet = bt.wallet(name=config.wallet.name, hotkey=config.wallet.hotkey, path=config.wallet.path, config=config)
axon = bt.axon(
    wallet=wallet,
    config=config,
    port=config.axon.port,
    ip=config.axon.ip,
    external_ip=config.axon.external_ip,
    external_port=config.axon.external_port,
    max_workers=config.axon.max_workers,
)

metagraph = bt.metagraph(netuid=config.netuid, network=config.subtensor.network, lite=True, sync=True)

validator = Validator(config=config, subtensor=subtensor, wallet=wallet, axon=axon, metagraph=subtensor.metagraph)
validator.save_state()
validator.wallet = wallet
validator.axon = axon
validator.subtensor = subtensor
validator.metagraph = metagraph
validator.config = config

validator.run()