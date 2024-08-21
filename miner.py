import json
import bittensor as bt
from getpass import getpass
from substrateinterface import Keypair
import os
import sys
import pickle
from utils.generated_config import main as config_main


from module_validator.chain.bittensor_subnet_template.neurons.miner import Miner as ExampleMiner


class Miner(ExampleMiner):
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

    def save_state(self):
          """Saves the state of the miner."""
          pass
    
    
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
    max_workers=config.axon.max_workers,
)
metagraph = bt.metagraph(netuid=config.netuid, network=config.subtensor.network, lite=True, sync=True)

print(metagraph.last_update)
miner = Miner(config=config, subtensor=subtensor, wallet=wallet, axon=axon, metagraph=subtensor.metagraph)
miner.wallet = wallet
miner.axon = axon
miner.subtensor = subtensor
miner.metagraph = metagraph
miner.config = config

miner.run()
