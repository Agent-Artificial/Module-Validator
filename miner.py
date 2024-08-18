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

from module_validator.chain.bittensor_subnet_template.neurons.miner import Miner as ExampleMiner


config = config_main()
print(config)

subtensor = bt.Subtensor(config.subtensor.network, config=config)
wallet = bt.wallet(name=config.wallet.name, hotkey=config.wallet.hotkey, path=config.wallet.path, config=config)
axon = bt.axon(
    wallet=wallet,
    config=config,
    port=config.axon.port,
    ip=config.axon.ip,
    external_ip=config.axon.external_ip,
    external_port=config.axon.external_port,
    max_workers=config.axon.max_workers
)
miner = ExampleMiner(config=config.model_dump())

miner.run()
