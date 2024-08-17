import bittensor as bt
from getpass import getpass
from substrateinterface import Keypair
from module_validator.chain.bittensor_subnet_template.docs.stream_tutorial.miner import StreamingTemplateMiner
from utils.configuration import main as config_main

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
miner = StreamingTemplateMiner(config=config, axon=axon, wallet=wallet, subtensor=subtensor)

miner.run()
