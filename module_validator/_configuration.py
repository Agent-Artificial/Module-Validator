from pydantic import BaseModel, Field
from typing import Any


from dotenv import load_dotenv
import os

load_dotenv()

class NeuronConfig(BaseModel):
    device: str = '"is_cuda_available()"'
    epoch_length: int = 100
    events_retention_size: str = '"2 * 1024 * 1024 * 1024"'
    dont_save_events: bool = False
    name: str = '"validator"'
    timeout: float = 10
    num_concurrent_forwards: int = 1
    sample_size: int = 50
    disable_set_weights: bool = False
    moving_average_alpha: float = 0.1
    vpermit_tao_limit: int = 4096


class WandbConfig(BaseModel):
    off: bool = False
    offline: bool = False
    notes: str = '""'
    project_name: str = '"template-validators"'
    entity: str = '"opentensor-dev"'


class BlacklistConfig(BaseModel):
    force_validator_permit: bool = False
    allow_non_registered: bool = False


class AxonConfig(BaseModel):
    port: int = "os.getenv('AXON_PORT', 7070)"


class SubtensorConfig(BaseModel):
    network: str = '"finney"'
    chain_endpoint: str = '"wss://entrypoint-finney.opentensor.ai:443"'


class MinerConfig(BaseModel):
    root: str = '"~/.bittensor/miners/"'
    name: str = '"Bittensor Miner"'
    blocks_per_epoch: str = '"100"'
    no_serve: bool = False
    no_start_axon: bool = False
    mock_subtensor: bool = False


class Config(BaseModel):
    Netuid: Any = Field(default=None)
    vpermit_tao_limit: int = Field(default=4096)
    Mock: Any = Field(default=None)
    entity: str = Field(default="opentensor-dev")
    allow_non_registered: bool = Field(default=False)
    Axon_off: Any = Field(default=None)
    port: int = "os.getenv('AXON_PORT', 7070)"
    chain_endpoint: str = Field(default="wss://entrypoint-finney.opentensor.ai:443")
    mock_subtensor: bool = Field(default=False)
    My_uid: Any = Field(default=None)
    Wallet_name: Any = Field(default=None)
    Hotkey: Any = Field(default=None)
    Network: Any = Field(default=None)
    Message: Any = Field(default=None)
    Name: Any = Field(default=None)
    File: Any = Field(default=None)
    neuron: NeuronConfig = Field(default_factory=NeuronConfig())
    wandb: WandbConfig = Field(default_factory=WandbConfig())
    blacklist: BlacklistConfig = Field(default_factory=BlacklistConfig())
    axon: AxonConfig = Field(default_factory=AxonConfig())
    subtensor: SubtensorConfig = Field(default_factory=SubtensorConfig())
    miner: MinerConfig = Field(default_factory=MinerConfig())

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
