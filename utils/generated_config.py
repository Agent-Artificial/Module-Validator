from typing import Any, Dict, Optional, Union, List
from substrateinterface import Keypair
from pydantic import BaseModel, Field, PrivateAttr, ConfigDict
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import bittensor as bt
import argparse
import json
import os
import yaml
import copy
import sys

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from munch import DefaultMunch


class Config(BaseModel):
    config: Optional[Union[Dict[str, Any], object]] = None
    _is_set: Dict[str, Dict[str, bool]] = PrivateAttr(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self._is_set = data.get('_is_set', {})

    def get(self, key: str, default: Any = ...) -> Any:
        keys = key.split('.')
        value = self
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            elif isinstance(value, BaseModel):
                value = getattr(value, k, None)
            else:
                return default if default is not ... else None
            if value is None:
                return default if default is not ... else None
        return value
    
    def is_set(self, key: str) -> bool:
        keys = key.split('.')
        is_set_dict = self._is_set
        for k in keys:
            if k not in is_set_dict:
                return False
            if isinstance(is_set_dict[k], bool):
                return is_set_dict[k]
            is_set_dict = is_set_dict[k]
        return True
    
    def set_is_set(self, key: str, value: bool):
        keys = key.split('.')
        is_set_dict = self._is_set
        for k in keys[:-1]:
            if k not in is_set_dict:
                is_set_dict[k] = {}
            is_set_dict = is_set_dict[k]
        is_set_dict[keys[-1]] = value
        
    @classmethod
    def merge(cls, a, b=None):
        if not b:
            b = {}
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge(a[key], b[key])
            else:
                a[key] = b[key]
        return a
    
    
class WalletConfig(Config):
    config: Optional[Any] = None
    name: str
    hotkey: Optional[str] = None
    path: str
    model_config: ConfigDict = ConfigDict(
        {"arbitrary_types_allowed": True}
    )
    

class AxonConfig(Config):
    config: Optional[Any] = None
    port: int
    ip: str
    external_ip: str
    external_port: int
    max_workers: int
    fast_server: Any = None


class SubtensorConfig(Config):
    config: Optional[Any] = None
    network: str
    chain_endpoint: str
    _mock: bool = PrivateAttr(default=False)
    
    def mock(self, value):
        if value:
            self._mock = value
        return self._mock


class MinerConfig(Config):
    config: Optional[Any] = None
    root: str
    name: str
    blocks_per_epoch: int
    no_serve: bool
    no_start_axon: bool
    mock_subtensor: bool
    full_path: str


class LoggingConfig(Config):
    config: Optional[Any] = None
    debug: bool
    trace: bool
    record_log: bool
    logging_dir: str


class WanDBConfig(Config):
    config: Optional[Any] = None
    notes: str = ""
    entity: str = ""
    offline: bool = True
    off: bool = False
    project_name: str = ""
    

class BlackListConfig(Config):
    config: Optional[Any] = None
    allow_non_registered: bool = False
    force_validator_permit: bool = False
    

class NeuronConfig(Config):
    config: Optional[Any] = None
    moving_average_alpha: float
    epoch_length: int
    num_concurrent_forwards: int
    axon_off: bool
    disable_set_weights: bool
    name: str
    device: str
    events_retention_size: int
    timeout: int
    sample_size: int
    dont_save_events: bool
    vpermit_tao_limit: int
    full_path: Optional[str] = None


class Configuration(Config):
    config: Optional[Any] = None
    axon: Optional[AxonConfig] = None
    wallet: Optional[WalletConfig] = None
    subtensor: Optional[SubtensorConfig] = None
    miner: Optional[MinerConfig] = None
    logging: Optional[LoggingConfig] = None
    wandb: Optional[WanDBConfig] = None
    blacklist: Optional[BlackListConfig] = None
    neuron: Optional[NeuronConfig] = None
    netuid: Optional[int] = None
    no_prompt: Optional[bool] = None
    strict: Optional[bool] = None
    mock: Optional[bool] = False
    no_version_checking: Optional[bool] = None
    model_config: ConfigDict = ConfigDict({
        "arbitrary_types_allowed": True
    })
    default_EXTERNAL_SERVER_ADDRESS: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
    
    
class bittensor_config(DefaultMunch):
    config: Configuration = Field(default_factory=Configuration)
    lines: List[Any] = []

    def __init__(self, parser=None, args=None, strict=False, default=None):
        super().__init__()

        if parser is None:
            parser = argparse.ArgumentParser(description="Bittensor Configuration")
        config = self.cli()
        print(config)
        parser = argparse.ArgumentParser(description="Bittensor Configuration")
        parser = self._add_args(parser)
        args = sys.argv[1:] if args is None else args
        
        self.config = config
        self.config.config = bt.config(parser)
        
        if args:

            config_params = self.__parse_args__(args, parser, False)

            # Load config from file if specified
            self._load_config_file(parser, args)

            # Parse arguments again with potential new defaults
            params = self.__parse_args__(args, parser, config_params.strict or strict)

            # Split params and add to config
            self.__split_params__(params, self.config)

            # Track which parameters are set
            self._track_set_parameters(parser, args, params)


    def __getitem__(self, key):
        return self.config.get(key)

    def __setitem__(self, key, value):
        keys = key.split('.')
        obj = self.config
        for k in keys[:-1]:
            if not hasattr(obj, k):
                setattr(obj, k, Configuration())
            obj = getattr(obj, k)
        setattr(obj, keys[-1], value)

    def get(self, key, default: Any = ...) -> Any:
        if not self.config:
            self.config = self.cli()
        if key == "config":
            return self.config
        if key in self.config._is_set:
            return self.config.get(key)
        self.config.__setattr__(key, default)
        return default

    def _track_set_parameters(self, parser, args, params):
        parser_no_defaults = copy.deepcopy(parser)
        parser_no_defaults.set_defaults(**{key: argparse.SUPPRESS for key in params.__dict__})
        params_no_defaults = self.__parse_args__(args, parser_no_defaults, False)
        self.config._is_set = {k: True for k, v in params_no_defaults.__dict__.items() if v != argparse.SUPPRESS}

    def _load_config_file(self, parser, args):
        if self.config is None:
            self.config = self.cli()
            self._add_args(parser, args)
        return self.config

    @staticmethod
    def __parse_args__(args, parser, strict):
        if not strict:
            params, unrecognized = parser.parse_known_args(args=args)
            for unrec in unrecognized:
                if unrec.startswith("--") and unrec[2:] in params.__dict__:
                    setattr(params, unrec[2:], True)
        else:
            params = parser.parse_args(args=args)
        return params

           
    @staticmethod
    def __split_params__(params, _config):
        for arg_key, arg_val in params.__dict__.items():
            keys = arg_key.split(".")
            head = _config
            for key in keys[:-1]:
                if not hasattr(head, key):
                    setattr(head, key, Configuration())
                head = getattr(head, key)
            setattr(head, keys[-1], arg_val)

    def __deepcopy__(self, memo):
        config_copy = bittensor_config()
        memo[id(self)] = config_copy
        for k, v in self.items():
            if k == 'config':
                config_copy.config = Configuration(**copy.deepcopy(v.__dict__, memo))
            else:
                setattr(config_copy, k, copy.deepcopy(v, memo))
        return config_copy

    def __str__(self):
        visible = copy.deepcopy(self.toDict())
        visible.pop("__parser", None)
        visible.pop("__is_set", None)
        return "\n" + yaml.dump(visible, sort_keys=False)

    def _add_args(self, parser: argparse.ArgumentParser):
        load_dotenv()
        parser.add_argument("--subtensor.network", default=f"{os.getenv('subtensor_network')}")
        parser.add_argument("--subtensor.chain_endpoint", default=f"{os.getenv('subtensor_chain_endpoint')}")
        parser.add_argument("--subtensor._mock", default=f"{os.getenv('subtensor__mock')}")
        parser.add_argument("--netuid", default=f"{os.getenv('netuid')}")
        parser.add_argument("--miner.name", default=f"{os.getenv('miner_name')}")
        parser.add_argument("--miner.blocks_per_epoch", default=f"{os.getenv('miner_blocks_per_epoch')}")
        parser.add_argument("--miner.no_serve", default=f"{os.getenv('miner_no_serve')}")
        parser.add_argument("--miner.no_start_axon", default=f"{os.getenv('miner_no_start_axon')}")
        parser.add_argument("--miner.mock_subtensor", default=f"{os.getenv('miner_mock_subtensor')}")
        parser.add_argument("--logging.debug", default=f"{os.getenv('logging_debug')}")
        parser.add_argument("--logging.trace", default=f"{os.getenv('logging_trace')}")
        parser.add_argument("--logging.record_log", default=f"{os.getenv('logging_record_log')}")
        parser.add_argument("--logging.logging_dir", default=f"{os.getenv('logging_logging_dir')}")
        parser.add_argument("--blacklist.allow_non_registered", default=f"{os.getenv('blacklist_allow_non_registered')}")
        parser.add_argument("--blacklist.force_validator_permit", default=f"{os.getenv('blacklist_force_validator_permit')}")
        parser.add_argument("--no_prompt", default=f"{os.getenv('no_prompt')}")
        parser.add_argument("--wallet.name", default=f"{os.getenv('wallet_name')}")
        parser.add_argument("--wallet.hotkey", default=f"{os.getenv('wallet_hotkey')}")
        parser.add_argument("--wallet.path", default=f"{os.getenv('wallet_path')}")
        parser.add_argument("--wandb.notes", default=f"{os.getenv('wandb_notes')}")
        parser.add_argument("--wandb.entity", default=f"{os.getenv('wandb_entity')}")
        parser.add_argument("--wandb.offline", default=f"{os.getenv('wandb_offline')}")
        parser.add_argument("--wandb.off", default=f"{os.getenv('wandb_off')}")
        parser.add_argument("--axon.port", default=f"{os.getenv('axon_port')}")
        parser.add_argument("--axon.ip", default=f"{os.getenv('axon_ip')}")
        parser.add_argument("--axon.external_port", default=f"{os.getenv('axon_port')}")
        parser.add_argument("--axon.external_ip", default=f"{os.getenv('axon_external_ip')}")
        parser.add_argument("--axon.max_workers", default=f"{os.getenv('axon_max_workers')}")
        parser.add_argument("--miner.full_path", default=f"{os.getenv('miner_full_path')}")
        parser.add_argument("--strict", default=f"{os.getenv('strict')}")
        parser.add_argument("--default.EXTERNAL_SERVER_ADDRESS", default=f"{os.getenv('default_EXTERNAL_SERVER_ADDRESS')}")
        return parser

    def _add_env_variables(self):
        self.lines = [
            f"BT_WALLET_PATH={self.config.wallet.path}",
            f"BT_AXON_PORT={self.config.axon.port}",
            f"BT_PRIORITY_MAX_WORKERS={self.config.axon.max_workers}",
            f"BT_WALLET_NAME={self.config.wallet.name}",
            f"BT_AXON_MAX_WORERS={self.config.axon.max_workers}",
            f"BT_AXON_EXTERNAL_IP={self.config.axon.external_ip}",
            f"BT_AXON_IP={self.config.axon.ip}",
            f"BT_AXON_EXTERNAL_PORT={self.config.axon.external_port}",
            f"BT_WALLET_HOTKEY={self.config.wallet.hotkey}",
            f"subtensor_network={self.config.subtensor.network}",
            f"subtensor_chain_endpoint={self.config.subtensor.chain_endpoint}",
            f"subtensor__mock={self.config.subtensor._mock}",
            f"netuid={self.config.netuid}",
            f"miner_name={self.config.miner.name}",
            f"miner_blocks_per_epoch={self.config.miner.blocks_per_epoch}",
            f"miner_no_serve={self.config.miner.no_serve}",
            f"miner_no_start_axon={self.config.miner.no_start_axon}",
            f"miner_mock_subtensor={self.config.miner.mock_subtensor}",
            f"miner_fll_path={self.config.miner.full_path}",
            f"logging_debug={self.config.logging.debug}",
            f"logging_trace={self.config.logging.trace}",
            f"logging_record_log={self.config.logging.record_log}",
            f"logging_logging_dir={self.config.logging.logging_dir}",            
            f'blacklist_allow_non_registered={self.config.blacklist.allow_non_registered}',
            f'blacklist_force_validator_permit={self.config.blacklist.force_validator_permit}',
            f"no_prompt={self.config.no_prompt}",
            f"wallet_name={self.config.wallet.name}",
            f"wallet_hotkey={self.config.wallet.hotkey}",
            f"wallet_path={self.config.wallet.path}",
            f"wandb_notes={self.config.wandb.notes}",
            f"wandb_entity={self.config.wandb.entity}",
            f"wandb_offline={self.config.wandb.offline}",
            f"wandb_off={self.config.wandb.off}",
            f"axon_port={self.config.axon.port}",
            f"axon_ip={self.config.axon.ip}",
            f"axon_external_port={self.config.axon.external_port}",
            f"axon_external_ip={self.config.axon.external_ip}",
            f"axon_max_workers={self.config.axon.max_workers}",
            f"default_EXTERNAL_SERVER_ADDRESS=https://{self.config.axon.external_ip}:{self.config.axon.external_port}"
            f"strict={self.config.strict}",
            "subtensor__mock=false",
            "subtensor_chain_endpoint=wss://test.finney.opentensor.ai:443",
            "DEBUG_MINER=None",
            "wallet_name=razor_test",
            "wallet_hotkey=razor_hot",
            "subtensor_network=test",
            "axon_external_ip=0.0.0.0",
            "axon_port=8080",
            "netuid=197",
            "axon_port=8080",
            "netuid=197",
            "DEBUG_MINER=None",
            "subtensor_network=test",
            "axon_external_ip=0.0.0.0",
            "subtensor_chain_endpoint=wss://test.finney.opentensor.ai:443",
            "wallet_name=razor_test",
            "wallet_hotkey=razor_hot",
        ]
        return self.lines

    def cli(self):
        load_dotenv()
        configure = input("Do you want to setup Bittensor configuration? (y/n) ")
        
        port = int(os.getenv("axon_port")) or 8080
        ip = os.getenv("axon_ip") or "0.0.0.0"
        external_ip = os.getenv("axon_external_ip") or "0.0.0.0"
        external_port = int(os.getenv("axon_external_port")) or 8080
        max_workers = int(os.getenv("axon_max_workers")) or 8
        network = os.getenv("subtensor_network") or "test"
        chain_endpoint = os.getenv("subtensor_chain_endpoint") or "wss://test.finney.opentensor.ai:443"
        root = os.getenv("miner_root") or f"{Path('~/.bittensor/miners/razor_test/').expanduser()}"
        name = os.getenv("miner_name") or "razor_hot"
        blocks_per_epoch = os.getenv("miner_blocks_per_epoch") or 100
        no_serve = os.getenv("miner_no_serve") or False
        no_start_axon = os.getenv("miner_no_start_axon") or False
        mock_subtensor = os.getenv("miner_mock_subtensor") or False
        full_path = os.getenv("full_path") or f"{Path('~/.bittensor/miners/razor_test/razor_hot/netuid197/razor_test').expanduser()}"
        debug = os.getenv("logging_debug") or True
        trace = os.getenv("logging_trace") or True
        record_log = os.getenv("logging_record_log") or True
        logging_dir = str(os.getenv("logging_logging_dir") or f"{Path('~/vscode/module_validator/.log').expanduser()}")
        notes = os.getenv("wandb_notes") or ""
        entity = os.getenv("wandb_entity") or ""
        offline = os.getenv("wandb_offline") or True
        off = os.getenv("wandb_off") or True
        project_name = os.getenv("wandb_project_name") or ""
        allow_non_registered = os.getenv("blacklist_allow_non_registered") or False
        force_validator_permit = os.getenv("blacklist_force_validator_permit") or False
        name = os.getenv("wallet_name") or "razor_test"
        hotkey = os.getenv("wallet_hotkey") or "razor_hot"
        path = str(os.getenv("wallet_path") or f"{Path('~/.bittensor/wallets').expanduser()}")
        netuid = int(os.getenv("netuid")) or 197
        no_prompt = bool(os.getenv("no_prompt")) or False
        strict = bool(os.getenv("strict")) or False
        no_version_checking = os.getenv("no_version_checking") or False
        default_EXTERNAL_SERVER_ADDRESS = os.getenv("default_EXTERNAL_SERVER_ADDRESS") or "https://0.0.0.0:8080"
        if configure.lower() == 'y':
            port = int(input("Enter axon port[8080]: ")) or port
            ip = input("Enter axon ip[0.0.0.0]: ") or ip
            external_ip = input("Enter axon external ip[0.0.0.0]: ") or external_ip
            external_port = int(input("Enter axon external port[8080]: ")) or external_port
            max_workers = int(input("Enter max workers[10]: ")) or max_workers
            network = input("Enter subtensor network(finney/[testnet]/local): ") or network
            chain_endpoint = input("Enter chain endpoint[wss://test.opentensor.ai:443]: ") or chain_endpoint
            root = input(f"Enter miner root[{Path('~/.bittensor/miners/razor_test/').expanduser()}]: ") or root
            name = input("Enter miner name[razor_hot]: ") or name
            blocks_per_epoch = int(input("Enter blocks per epoch[100]: ")) or blocks_per_epoch
            no_serve = bool(input("Enter no_serve[False]: ")) or no_serve
            no_start_axon = bool(input("Enter no_start_axon[False]: ")) or no_start_axon
            mock_subtensor = bool(input("Enter mock_subtensor[False]: ")) or mock_subtensor
            full_path = input(f"Enter full_path[{Path('~/.bittensor/miners/razor_test/razor_hot/netuid197/razor_test').expanduser()}]: ") or full_path
            debug = bool(input("Enter debug[True]: ")) or debug
            trace = bool(input("Enter trace[True]: ")) or trace
            record_log = bool(input("Enter record_log[True]: ")) or record_log
            logging_dir = str(input(f"Enter logging_dir[{Path('~/vscode/module_validator/.log').expanduser()}]: ")) or logging_dir
            allow_non_registered = bool(input("Enter allow_non_registered[False]: ")) or allow_non_registered
            force_validator_permit = bool(input("Enter force_validator_permit[False]: ")) or force_validator_permit
            notes = input("Enter wandb notes['']: ") or notes
            entity = input("Enter wandb entity['']: ") or entity
            offline = input("Enter wandb offline[True]: ") or offline
            off = input("Enter wandb off[True]): ") or off
            name = input("Enter wallet name[razor_test]: ") or name
            hotkey = input("Enter wallet hotkey[razor_hot]: ") or hotkey
            path = str(input(f"Enter wallet path[{Path('~/.bittensor/wallets').expanduser()}]: ")) or path
            netuid = int(input("Enter netuid[197]: ")) or netuid
            no_prompt = bool(input("Enter no_prompt[False]: ")) or no_prompt
            strict = bool(input("Enter strict[False]: ")) or strict
            no_version_checking = bool(input("Enter no_version_checking[False]: ")) or no_version_checking
            default_EXTERNAL_SERVER_ADDRESS = default_EXTERNAL_SERVER_ADDRESS
        return Configuration(
            config=None,
            axon=AxonConfig(
                config=None,
                port=port,
                ip=ip,
                external_ip=external_ip,
                external_port=external_port,
                max_workers=max_workers
            ),
            subtensor=SubtensorConfig(
                config=None,
                network=network,
                chain_endpoint=chain_endpoint,
                fast_server=None,
            ),
            miner=MinerConfig(
                config=None,
                root=root,
                name=name,
                blocks_per_epoch=blocks_per_epoch,
                no_serve=no_serve,
                no_start_axon=no_start_axon,
                mock_subtensor=mock_subtensor,
                full_path=full_path
            ),
            logging=LoggingConfig(
                config=None,
                debug=debug,
                trace=trace,
                record_log=record_log,
                logging_dir=logging_dir,
            ),
            blacklist=BlackListConfig(
                config=None,
                allow_non_registered=allow_non_registered,
                force_validator_permit=force_validator_permit,
            ),
            wandb=WanDBConfig(
                config=None,
                notes=notes,
                entity=entity,
                offline=offline,
                off=off,
                project_name=project_name,
            ),
            wallet=WalletConfig(
                config=None,
                name=name,
                hotkey=hotkey,
                path=path,
            ),
            netuid=netuid,
            no_prompt=no_prompt,
            strict=strict,
            no_version_checking=no_version_checking,
            default_external_server_address=default_EXTERNAL_SERVER_ADDRESS,
        )

    def get_hotkey(self, wallet_name: str, hotkey_name: str):
        path = Path("~/.bittensor/wallets").expanduser()
        key_path = path / wallet_name / "hotkeys" / hotkey_name
        key_data = json.loads(key_path.read_text())
        public_key = key_data["publicKey"]
        private_key = key_data["privateKey"]
        ss58key = key_data["ss58Address"]
        return Keypair(ss58_address=ss58key, private_key=private_key, public_key=public_key)
        
    def write_environment(self, config):
        settings = config
        settings_dict = {}
        if isinstance(settings, Configuration):
            settings = settings.__dict__

        env_dict = {}

        for key, value in settings.items():
            if isinstance(value, Configuration):
                value = value.dict()
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    env_dict[f"{key}_{subkey}"] = subvalue
            else:
                env_dict[key] = value

        lines = [f"{key}={value}\n" for key, value in env_dict.items()]
        lines.extend([f"{variable}\n" for variable in self._add_env_variables()])
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(lines)
        return settings_dict


def main():
    parser = argparse.ArgumentParser(description="bittensor configuration")
    return bittensor_config(parser=parser)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    configuration = bittensor_config(parser=parser)