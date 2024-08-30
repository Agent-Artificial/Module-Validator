from pydantic import BaseModel, Field
from typing import Any, Union, Dict, List, Optional, ClassVar
from pydantic import ConfigDict
from dotenv import load_dotenv
from module_validator.config.base_configuration import GenericConfig, T
import bittensor as bt
import argparse
import os

load_dotenv()


class AxonConfig(GenericConfig):
    port: int = Field({'name': 'axon.port', 'default': 8098, 'type': 'int', 'help': 'Port to run the axon on.', 'action': None})

    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        

class SubtensorConfig(GenericConfig):
    network: None = Field({'name': 'subtensor.network', 'default': 'finney', 'type': None, 'help': 'Bittensor network to connect to.', 'action': None})
    chain_endpoint: None = Field({'name': 'subtensor.chain_endpoint', 'default': 'wss://entrypoint-finney.opentensor.ai:443', 'type': None, 'help': 'Chain endpoint to connect to.', 'action': None})

    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        

class MinerConfig(GenericConfig):
    root: str = Field({'name': 'miner.root', 'default': '~/.bittensor/miners/', 'type': 'str', 'help': 'Trials for this miner go in miner.root / (wallet_cold - wallet_hot) / miner.name', 'action': None})
    name: str = Field({'name': 'miner.name', 'default': 'Bittensor Miner', 'type': 'str', 'help': 'Trials for this miner go in miner.root / (wallet_cold - wallet_hot) / miner.name', 'action': None})
    blocks_per_epoch: str = Field({'name': 'miner.blocks_per_epoch', 'default': 100, 'type': 'str', 'help': 'Blocks until the miner repulls the metagraph from the chain', 'action': None})
    no_serve: None = Field({'name': 'miner.no_serve', 'default': False, 'type': None, 'help': 'If True, the miner doesnt serve the axon.', 'action': None})
    no_start_axon: None = Field({'name': 'miner.no_start_axon', 'default': False, 'type': None, 'help': 'If True, the miner doesnt start the axon.', 'action': None})
    mock_subtensor: None = Field({'name': 'miner.mock_subtensor', 'default': False, 'type': None, 'help': 'If True, the miner will allow non-registered hotkeys to mine.', 'action': None})

    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        

class NeuronConfig(GenericConfig):
    device: str = Field({'name': 'neuron.device', 'default': 'is_cuda_available()', 'type': 'str', 'help': 'Device to run on.', 'action': None})
    epoch_length: int = Field({'name': 'neuron.epoch_length', 'default': 100, 'type': 'int', 'help': 'The default epoch length (how often we set weights, measured in 12 second blocks).', 'action': None})
    events_retention_size: str = Field({'name': 'neuron.events_retention_size', 'default': '2 * 1024 * 1024 * 1024', 'type': 'str', 'help': 'Events retention size.', 'action': None})
    dont_save_events: None = Field({'name': 'neuron.dont_save_events', 'default': False, 'type': None, 'help': 'If set, we dont save events to a log file.', 'action': None})
    name: str = Field({'name': 'neuron.name', 'default': 'validator', 'type': 'str', 'help': 'Trials for this neuron go in neuron.root / (wallet_cold - wallet_hot) / neuron.name.', 'action': None})
    timeout: float = Field({'name': 'neuron.timeout', 'default': 10, 'type': 'float', 'help': 'The timeout for each forward call in seconds.', 'action': None})
    num_concurrent_forwards: int = Field({'name': 'neuron.num_concurrent_forwards', 'default': 1, 'type': 'int', 'help': 'The number of concurrent forwards running at any time.', 'action': None})
    sample_size: int = Field({'name': 'neuron.sample_size', 'default': 50, 'type': 'int', 'help': 'The number of miners to query in a single step.', 'action': None})
    disable_set_weights: None = Field({'name': 'neuron.disable_set_weights', 'default': False, 'type': None, 'help': 'Disables setting weights.', 'action': None})
    moving_average_alpha: float = Field({'name': 'neuron.moving_average_alpha', 'default': 0.1, 'type': 'float', 'help': 'Moving average alpha parameter, how much to add of the new observation.', 'action': None})
    axon_off: None = Field({'name': 'neuron.axon_off', 'default': False, 'type': None, 'help': 'Set this flag to not attempt to serve an Axon.', 'action': None})
    vpermit_tao_limit: int = Field({'name': 'neuron.vpermit_tao_limit', 'default': 4096, 'type': 'int', 'help': 'The maximum number of TAO allowed to query a validator with a vpermit.', 'action': None})

    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        

class WandbConfig(GenericConfig):
    off: None = Field({'name': 'wandb.off', 'default': False, 'type': None, 'help': 'Turn off wandb.', 'action': None})
    offline: None = Field({'name': 'wandb.offline', 'default': False, 'type': None, 'help': 'Runs wandb in offline mode.', 'action': None})
    notes: str = Field({'name': 'wandb.notes', 'default': '', 'type': 'str', 'help': 'Notes to add to the wandb run.', 'action': None})
    project_name: str = Field({'name': 'wandb.project_name', 'default': 'template-validators', 'type': 'str', 'help': 'The name of the project where you are sending the new run.', 'action': None})
    entity: str = Field({'name': 'wandb.entity', 'default': 'opentensor-dev', 'type': 'str', 'help': 'The name of the project where you are sending the new run.', 'action': None})

    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        

class BlacklistConfig(GenericConfig):
    force_validator_permit: None = Field({'name': 'blacklist.force_validator_permit', 'default': False, 'type': None, 'help': 'If set, we will force incoming requests to have a permit.', 'action': None})
    allow_non_registered: None = Field({'name': 'blacklist.allow_non_registered', 'default': False, 'type': None, 'help': 'If set, miners will accept queries from non registered entities. (Dangerous!)', 'action': None})

    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        


class Config(GenericConfig):
    model_config: ClassVar[ConfigDict] = ConfigDict({
            "aribtrary_types_allowed": True
    })
    config: Optional[bt.config] = Field(default_factory=bt.config, type=None)
    axon: Optional[bt.axon] = Field(default_factory=bt.axon, type=None)
    wallet: Optional[bt.wallet] = Field(default_factory=bt.wallet, type=None)
    metagraph: Optional[T] = Field(default_factory=bt.metagraph, type=None)
    subtensor: Optional[bt.subtensor] = Field(default_factory=bt.subtensor, type=None)
    dendrite: Optional[bt.dendrite] = Field(default_factory=bt.dendrite, type=None)
    hotkeypair: Optional[bt.Keypair] = Field(default_factory=bt.Keypair, type=None)
    netuid: int = Field({'name': 'netuid', 'default': 1, 'type': 'int', 'help': 'Subnet netuid', 'action': None})
    my_uid: int = Field({'name': 'my_uid', 'default': None, 'type': 'int', 'help': 'Your unique miner ID on the chain', 'action': None})
    wallet_name: str = Field({'name': 'wallet_name', 'default': 'default', 'type': 'str', 'help': 'Name of the wallet', 'action': None})
    hotkey: str = Field({'name': 'hotkey', 'default': 'default', 'type': 'str', 'help': 'Hotkey for the wallet', 'action': None})
    network: str = Field({'name': 'network', 'default': 'test', 'type': 'str', 'help': 'Network type, e.g., "test" or "mainnet"', 'action': None})
    mock: None = Field({'name': 'mock', 'default': False, 'type': None, 'help': 'Mock neuron and all network components.', 'action': None})
    message: str = Field({'name': 'message', 'default': None, 'type': 'str', 'help': 'The message to sign', 'action': None})
    name: str = Field({'name': 'name', 'default': None, 'type': 'str', 'help': 'The wallet name', 'action': None})
    file: None = Field({'name': 'file', 'default': None, 'type': None, 'help': 'The file containing the message and signature', 'action': None})
    ax: AxonConfig = Field(default_factory=AxonConfig, )
    subtensor: SubtensorConfig = Field(default_factory=SubtensorConfig, )
    miner: MinerConfig = Field(default_factory=MinerConfig, )
    neur: NeuronConfig = Field(default_factory=NeuronConfig, )
    wandb: WandbConfig = Field(default_factory=WandbConfig, )
    blacklist: BlacklistConfig = Field(default_factory=BlacklistConfig, )

    
    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        model_config: ConfigDict = ConfigDict({
            "aribtrary_types_allowed": True
        })

    def get(self, key: str, default: T = None) -> T:
        return self._get(key, default)
    
    def set(self, key: str, value: T) -> None:
        self._set(key, value)
        
    def merge(self, new_config: Dict[str, T]) -> Dict[str, Any]:
        self.config = self._merge(new_config, self.config)
        return self.config

    def load_config(self, parser: argparse.ArgumentParser, args: argparse.Namespace) -> 'Config':
        return self._load_config(parser, args)
    
    def parse_args(self, args: argparse.Namespace):
        self._parse_args(args)
    
    def add_args(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        return self._add_args(parser)
    
    def get_env(self) -> List[str]:
        lines = [
            f'neuron.events_retention_size=2 * 1024 * 1024 * 1024',
            f'neuron.dont_save_events=False',
            f'blacklist.force_validator_permit=False',
            f'neuron.axon_off=False',
            f'neuron.device=is_cuda_available()',
            f'miner.root=~/.bittensor/miners/',
            f'neuron.num_concurrent_forwards=1',
            f'subtensor.chain_endpoint=wss://entrypoint-finney.opentensor.ai:443',
            f'miner.no_start_axon=False',
            f'wandb.offline=False',
            f'neuron.moving_average_alpha=0.1',
            f'wandb.project_name=template-validators',
            f'blacklist.allow_non_registered=False',
            f'netuid=1',
            f'neuron.timeout=10',
            f'wandb.notes=',
            f'hotkey=default',
            f'neuron.epoch_length=100',
            f'miner.name=Bittensor Miner',
            f'wandb.entity=opentensor-dev',
            f'neuron.disable_set_weights=False',
            f'miner.no_serve=False',
            f'wallet_name=default',
            f'miner.blocks_per_epoch=100',
            f'axon.port=8098',
            f'miner.mock_subtensor=False',
            f'network=test',
            f'neuron.name=validator',
            f'neuron.sample_size=50',
            f'wandb.off=False',
            f'mock=False',
            f'neuron.vpermit_tao_limit=4096',
            f'subtensor.network=finney',

        ]
        return self._add_env(self.config)

    def add_args(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        parser.add_argument('--config', type=str, default=None, help='path to config file', required=False)
        parser.add_argument("--axon.port", default="8098", type=int, help="Port to run the axon on.", action="None")
        parser.add_argument("--subtensor.network", default="finney", type=str, help="Bittensor network to connect to.", action="None")
        parser.add_argument("--subtensor.chain_endpoint", default="wss://entrypoint-finney.opentensor.ai:443", type=str, help="Chain endpoint to connect to.", action="None")
        parser.add_argument("--netuid", default="1", type=int, help="Subnet netuid", action="None")
        parser.add_argument("--miner.root", default="~/.bittensor/miners/", type=str, help="Trials for this miner go in miner.root / (wallet_cold - wallet_hot) / miner.name", action="None")
        parser.add_argument("--miner.name", default="Bittensor Miner", type=str, help="Trials for this miner go in miner.root / (wallet_cold - wallet_hot) / miner.name", action="None")
        parser.add_argument("--miner.blocks_per_epoch", default="100", type=str, help="Blocks until the miner repulls the metagraph from the chain", action="None")
        parser.add_argument("--miner.no_serve", default="None", type=str, help="If True, the miner doesnt serve the axon.", action="None")
        parser.add_argument("--miner.no_start_axon", default="None", type=str, help="If True, the miner doesnt start the axon.", action="None")
        parser.add_argument("--miner.mock_subtensor", default="None", type=str, help="If True, the miner will allow non-registered hotkeys to mine.", action="None")
        parser.add_argument("--my_uid", default="None", type=int, help="Your unique miner ID on the chain", action="None")
        parser.add_argument("--wallet_name", default="default", type=str, help="Name of the wallet", action="None")
        parser.add_argument("--hotkey", default="default", type=str, help="Hotkey for the wallet", action="None")
        parser.add_argument("--network", default="test", type=str, help="Network type, e.g., "test" or "mainnet"", action="None")
        parser.add_argument("--neuron.device", default="is_cuda_available()", type=str, help="Device to run on.", action="None")
        parser.add_argument("--neuron.epoch_length", default="100", type=int, help="The default epoch length (how often we set weights, measured in 12 second blocks).", action="None")
        parser.add_argument("--mock", default="None", type=str, help="Mock neuron and all network components.", action="None")
        parser.add_argument("--neuron.events_retention_size", default="2 * 1024 * 1024 * 1024", type=str, help="Events retention size.", action="None")
        parser.add_argument("--neuron.dont_save_events", default="None", type=str, help="If set, we dont save events to a log file.", action="None")
        parser.add_argument("--wandb.off", default="None", type=str, help="Turn off wandb.", action="None")
        parser.add_argument("--wandb.offline", default="None", type=str, help="Runs wandb in offline mode.", action="None")
        parser.add_argument("--wandb.notes", default="None", type=str, help="Notes to add to the wandb run.", action="None")
        parser.add_argument("--neuron.name", default="validator", type=str, help="Trials for this neuron go in neuron.root / (wallet_cold - wallet_hot) / neuron.name.", action="None")
        parser.add_argument("--blacklist.force_validator_permit", default="None", type=str, help="If set, we will force incoming requests to have a permit.", action="None")
        parser.add_argument("--blacklist.allow_non_registered", default="None", type=str, help="If set, miners will accept queries from non registered entities. (Dangerous!)", action="None")
        parser.add_argument("--wandb.project_name", default="template-validators", type=str, help="The name of the project where you are sending the new run.", action="None")
        parser.add_argument("--wandb.entity", default="opentensor-dev", type=str, help="The name of the project where you are sending the new run.", action="None")
        parser.add_argument("--neuron.timeout", default="10", type=float, help="The timeout for each forward call in seconds.", action="None")
        parser.add_argument("--neuron.num_concurrent_forwards", default="1", type=int, help="The number of concurrent forwards running at any time.", action="None")
        parser.add_argument("--neuron.sample_size", default="50", type=int, help="The number of miners to query in a single step.", action="None")
        parser.add_argument("--neuron.disable_set_weights", default="None", type=str, help="Disables setting weights.", action="None")
        parser.add_argument("--neuron.moving_average_alpha", default="0.1", type=float, help="Moving average alpha parameter, how much to add of the new observation.", action="None")
        parser.add_argument("--neuron.axon_off", default="None", type=str, help="Set this flag to not attempt to serve an Axon.", action="None")
        parser.add_argument("--neuron.vpermit_tao_limit", default="4096", type=int, help="The maximum number of TAO allowed to query a validator with a vpermit.", action="None")
        parser.add_argument("--message", default="None", type=str, help="The message to sign", action="None")
        parser.add_argument("--name", default="None", type=str, help="The wallet name", action="None")
        parser.add_argument("--file", default="None", type=str, help="The file containing the message and signature", action="None")

        return parser


