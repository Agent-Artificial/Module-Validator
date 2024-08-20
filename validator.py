import uvicorn.config
from utils.generated_config import main as config_main
from pathlib import Path
from substrateinterface import Keypair
from bittensor.axon import FastAPIThreadedServer
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import argparse
import bittensor as bt
import subprocess
import json
import os
import sys


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_hotkey(config):
    wallet_hotkey = os.getenv("BT_WALLET_HOTKEY")
    wallet_name = os.getenv("BT_WALLET_NAME")
    path = Path(config.wallet.path)
    key_path = path / wallet_name / "hotkeys" / wallet_hotkey
    key_data = json.loads(key_path.read_text())
    public_key = key_data["publicKey"]
    private_key = key_data["privateKey"]
    ss58_address = key_data["ss58Address"]
    return Keypair(ss58_address=ss58_address, private_key=private_key, public_key=public_key)


bittensor_configuration = config_main()

bt_config = bittensor_configuration.config  #  bt.config(parser=bittensor_configuration._add_args(parser=argparse.ArgumentParser()))

print(bt_config)

bt_config.axon.config = bt_config.config
bt_config.wallet.config = bt_config.config
bt_config.wallet.hotkey = bt_config.wallet.hotkey
bt_config.subtensor.config = bt_config.config
bt_config.blacklist.config = bt_config.config
bt_config.wallet.config = bt_config.config
bt_config.wandb.config = bt_config.config


# bt_config.axon.fast_server = FastAPIThreadedServer(uvicorn.Config(app=app, host=bt_config.axon.ip, port=bt_config.axon.port))
wallet = bt.wallet(name=bt_config.wallet.name, hotkey=get_hotkey(bt_config), path=bt_config.wallet.path, config=bt_config)
subtensor = bt.subtensor(network=bt_config.subtensor.network, config=bt_config, _mock=False, log_verbose=True)
axon = bt.axon(wallet=wallet, config=bt_config, port=bt_config.axon.port, ip=bt_config.axon.ip, external_ip=bt_config.axon.external_ip, external_port=bt_config.axon.external_port, max_workers=bt_config.axon.max_workers)
metagraph = bt.metagraph(netuid=bt_config.netuid, network=bt_config.subtensor.network, lite=True, sync=True)

config = bt_config.config
print(config)
parser = argparse.ArgumentParser()

os.chdir("module_validator/chain/vision/")

from validation.core_validator import CoreValidator


parser.add_argument("--env_file", default=".env", type=str)


validator = CoreValidator(config=config, parser=parser)

validator.run()

# print("Current working directory:", os.getcwd())
# command = [
#     "python",
#     "-m",
#     # "uvicorn",
#     "validation.proxy.api_server.asgi",
#     # "--host",
#     # f"{config.axon.ip}",
#     # "--port",
#     # f"{config.axon.port}",
#     "--env_file",
#     ".env",
#     "--config",
#     f"{config}"
#     "--subtensor.network",
#     f"{config.subtensor.network}",
#     "--subtensor.chain_endpoint",
#     f"{config.subtensor.chain_endpoint}",
#     "--netuid",
#     f"{config.netuid}",
#     "--miner.name",
#     f"{config.miner.name}",
#     "--miner.blocks_per_epoch",
#     f"{config.miner.blocks_per_epoch}",
#     "--logging.debug",
#     "--logging.trace",
#     "--logging.record_log",
#     "--logging.logging_dir",
#     f"{os.getenv('logging_dir')}",
#     "--wallet.name",
#     f"{config.wallet.name}",
#     "--wallet.hotkey",
#     f"{config.wallet.hotkey}",
#     "--wallet.path",
#     f"{config.wallet.path}",
#     "--axon.port",
#     f"{config.axon.port}",
#     "--axon.ip",
#     f"{config.axon.ip}",
#     "--axon.external_port",
#     f"{config.axon.external_port}",
#     "--axon.external_ip",
#     f"{config.axon.external_ip}",
#     "--axon.max_workers",
#     f"{config.axon.max_workers}",
#     "--miner.full_path",
#     f"{config.miner.full_path}"
#     "--default.external_server_address",
#     f"{config.default.EXTERNAL_SERVER_ADDRESS}",
# ]

# result = subprocess.run(command)



