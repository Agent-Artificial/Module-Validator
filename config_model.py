from pydantic import BaseModel, Field
from typing import Any, Dict
import bittensor as bt

from bittensor.wallet import wallet
from bittensor.extrinsics.set_weights import set_weights_extrinsic
from bittensor.extrinsics.serving import serve_axon_extrinsic, serve_extrinsic
from bittensor.dendrite import dendrite
from bittensor.axon import axon
from bittensor.config import DefaultConfig
from bittensor.btlogging.loggingmachine import LoggingMachine, LoggingConfig
from bittensor.cli import COMMANDS
from bittensor.subtensor import Subtensor
from bittensor.metagraph import TorchMetaGraph
from bittensor.axon import AxonMiddleware
from bittensor.subtensor import subtensor
from bittensor.utils.weight_utils import convert_weight_uids_and_vals_to_tensor, convert_weights_and_uids_for_emit

print(COMMANDS)

from dotenv import load_dotenv
import os

load_dotenv()

class NeuronConfig(BaseModel):
    device: str = 'cuda()'
    epoch_length: int = 1000
    events_retention_size: str = 2147483647
    dont_save_events: bool = False
    name: str = 'razor_test'
    timeout: float = 10
    num_concurrent_forwards: int = 4
    sample_size: int = 50
    disable_set_weights: bool = False
    moving_average_alpha: float = 0.1
    vpermit_tao_limit: int = 4096

class WandbConfig(BaseModel):
    off: bool = True
    offline: bool = True
    notes: str = ''
    project_name: str = ''
    entity: str = ''

class BlacklistConfig(BaseModel):
    force_validator_permit: bool = True
    allow_non_registered: bool = False

class AxonConfig(axon):
    port: int = 8080

class SubtensorConfig(BaseModel):
    network: str = "test"
    chain_endpoint: str = 'wss://test.finney.opentensor.ai:443'

class MinerConfig(BaseModel):
    root: str = '/home/bakobi/.bittensor/miners'
    name: str = 'miner'
    blocks_per_epoch: str = '1000'
    no_serve: bool = 'False'
    no_start_axon: bool = 'False'
    mock_subtensor: bool = 'False'

class Config(BaseModel):
    netuid: Any = 197
    neuron: Any = NeuronConfig(
        
    )
    mock: Any = False
    wandb: Any = WandbConfig()
    blacklist: Any = BlacklistConfig()
    axon_off: Any = False
    axon: Any = AxonConfig()
    subtensor: Any = SubtensorConfig()
    miner: Any = MinerConfig()
    my_uid: Any = 1
    wallet_name: Any = "razor_test"
    hotkey: Any = "razor_hot"
    network: Any = "test"
    message: Any = {"role": "admin", "message": "hello"}
    name: Any = miner
    file: Any = None
    netuid: bool = False
    
    mock: bool = False
    wandb: WandbConfig = WandbConfig()
    blacklist: BlacklistConfig = BlacklistConfig()
    axon_off: bool = False
    axon: int = int(f"{os.getenv('BT_AXON_PORT')}" or 8080)
    subtensor: SubtensorConfig = SubtensorConfig()
    my_uid: int = os.getenv('my_uid') or 8080
    miner: str = os.getenv("wallet_name") or "razor_test"
    
    wallet_name: str = os.getenv("wallet_name")
    hotkey: int = os.getenv('wallet_hotkey') or 8080
    network: int = os.getenv('subtensor_network') or 8080
    message: Dict[str, Any] = {"role": "system", "content": "some content"}
    name: str = os.getenv("wallet_name") or "razor_test"
    file: str = os.getenv("file") or 0

    def get(self, key: str, default: Any = None) -> Any:
        parts = key.split('.')
        value = self
        for part in parts:
            if isinstance(value, BaseModel):
                value = getattr(value, part, default)
            elif isinstance(value, dict):
                value = value.get(part, default)
            else:
                return default
            if value is None:
                return default
        return value
