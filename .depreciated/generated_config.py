from typing import Any, Dict, Optional, Union, List, Generic, TypeVar, ClassVar, Type, Callable, Tuple
from substrateinterface import Keypair
from pydantic import BaseModel, Field, PrivateAttr, ConfigDict
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import bittensor as bt
from bittensor.axon import FastAPIThreadedServer
import os
validator_dir = Path(__file__).parent.parent
sylliba_dir = validator_dir / "module_validator" / "chain" / "sylliba"
os.chdir(sylliba_dir)
from module_validator.chain.sylliba.sylliba import __version__
import uvicorn
import argparse
import json

import yaml
import copy
import sys

load_dotenv()

T = TypeVar('T')
GenericConfig = TypeVar('GenericConfig', bound=Type[BaseModel])
CallableType = TypeVar('CallableType', bound=Callable[..., Any])
GenericType = TypeVar('GenericType', bound=Type[T])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenericConfig(BaseModel, GenericConfig):
    config: Optional[Union[Dict[str, Any], object]] = Field(default_factory=dict)
    parser: Optional[argparse.ArgumentParser] = Field(default_factory=argparse.ArgumentParser)
    args: Optional[argparse.Namespace] = Field(default_factory=argparse.Namespace)
    bt_config: Optional[Union[Dict[str, Any], object]] = Field(default_factory=dict)
    lines: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__()
        self.config = self.model_dump()
        self.parser = self._load_parser()
        self.args = self.parser.parse_args()
        self._add_args(self.parser, self.args)
        self._merge(self.parser, self.args)
        self._add_env(self.config)
        self._load_config_file(self.parser, self.args)
        self.lines = self.dict_to_env_lines(self.config)
        
        self.bt_config = self.load_bt_config(parser)
    

    

    
    @classmethod
    def add_args(self, parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
        return self._add_args(parser, args)
        

    @classmethod
    def _parse_args(cls, parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
        pass

    @classmethod
    def _set_defaults(cls, parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
        pass

    @classmethod
    def _set_args(cls, parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
        pass


    @classmethod
    def load_config(cls, parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
        cls._load_config(parser, args)
    


    @classmethod
    def _merge_config(cls, a, b=None):
        if not b:
            b = {}
        if isinstance(a, dict) and isinstance(b, dict) and len(b.items() >= 1):
            for key_b in b:
                for key_a, value_a in 
                
                for key_a, value_b in b
                
            else:
                a[key] = b[key]
        return a

    @classmethod
    def merge_cli(cls, a, b=None):
        if not b:
            b = {}
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge_cli(a[key], b[key])
            else:
                a[key] = b[key]
        return a

    @classmethod
    def merge_args(cls, a, b=None):
        if not b:
            b = {}
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge_args(a[key], b[key])
            else:
                a[key] = b[key]
        return a

    @classmethod
    def merge_config_file(cls, a, b=None):
        if not b:
            b = {}
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge_config_file(a[key], b[key])
            else:
                a[key] = b[key]
        return a

    @classmethod
    def merge_config_and_cli(cls, a, b=None):
        if not b:
            b = {}
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge_config_and_cli(a[key], b[key])
            else:
                a[key] = b[key]
        return a

    @classmethod
    def merge_config_and_args(cls, a, b=None):
        if not b:
            b = {}
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge_config_and_args(a[key], b[key])
            else:
                a[key] = b[key]
        return a

    @classmethod
    def merge_config_and_cli_and_args(cls, a, b=None):
        if not b:
            b = {}
        for key in b:
            if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
                cls.merge_config_and_cli_and_args(a[key], b[key])
            else:
                a[key] = b[key]
        return a



    @classmethod
    def _get(cls, key: str, default: T = ...) -> GenericConfig[T]:
        keys = key.split('.')
        value = cls.model_dump()
        for k in keys:
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == k.lower():
                        value = v
                        break
            elif isinstance(value, BaseModel):
                value = getattr(value, k, None)
            else:
                return default if default is not ... else None
        return value

    @classmethod
    def _is_set(cls, key: str) -> bool:
        keys = key.split('.')
        is_set_dict = cls._is_set
        for k in keys:
            if k not in is_set_dict:
                return False
            if isinstance(is_set_dict[k], bool):
                return is_set_dict[k]
            is_set_dict = is_set_dict[k]
        return True
    
    @classmethod
    def _set_is_set(cls, key: str, value: bool):
        keys = key.split('.')
        is_set_dict = cls._is_set
        for k in keys[:-1]:
            if k not in is_set_dict:
                is_set_dict[k] = {}
            is_set_dict = is_set_dict[k]
        is_set_dict[keys[-1]] = bool(value)
                
    @classmethod
    def _set(cls, key: str, value: Any):
        keys = key.split('.')
        is_set_dict = cls._is_set
        length = len(keys)
        for i, k in enumerate(keys):
            if i == length - 1:
                cls.__setitems__(keys, value)
            else: 
                if k not in is_set_dict:
                    cls.__setitems__(keys[:i+1], {})
                cls.__setitems__(keys[:i+1], {k: {}})
        

    
    @classmethod
    def __getitem__(cls, key):
        return cls.config.get(key)

    @classmethod
    def __setitem__(cls, key, value):
        keys = key.split('.')
        obj = cls.config
        for k in keys[:-1]:
            if not hasattr(obj, k):
                setattr(obj, k, cls)
            obj = getattr(obj, k)
        setattr(obj, keys[-1], value)

    @classmethod
    def _track_set_parameters(cls, parser, args, params):
        parser_no_defaults = copy.deepcopy(parser)
        parser_no_defaults.set_defaults(**{key: argparse.SUPPRESS for key in params.__dict__})
        params_no_defaults = cls.__parse_args__(args, parser_no_defaults, False)
        cls.config._is_set = {k: True for k, v in params_no_defaults.__dict__.items() if v != argparse.SUPPRESS}

    @classmethod
    def _load_config_file(cls, parser, args):
        if cls.config is None:
            cls.config = cls.cli()
            cls._add_args(parser, args)
        return cls.config

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
                    setattr(head, key, GenericConfig())
                head = getattr(head, key)
            setattr(head, keys[-1], arg_val)

    @staticmethod
    def __deepcopy__(obj, memo):
        if isinstance(obj, GenericConfig) or isinstance(obj, BaseModel):
            obj = obj.model_dump()
        if not isinstance(obj, dict):
            raise ValueError(f"Deepcopy of {type(obj)} is not supported.")
        config_copy = GenericConfig()
        memo[id(obj)] = config_copy
        for k, v in obj.items():
            if k == 'config':
                config_copy.config = GenericConfig(**copy.deepcopy(v.__dict__, memo))
            else:
                setattr(config_copy, k, copy.deepcopy(v, memo))
        return config_copy


        


    def _prompt_for_value(self, config_dict=None):
        new_dict = {}
        if not config_dict:
            config_dict = self.config
        for key, value in config_dict.items():
            if isinstance(value, GenericConfig):
                value = value.model_dump()
                for subkey, subvalue in value.items():
                    config_dict = input(f"Enter value for {key}[{subkey or 'No default'}]: ") or subkey
                    new_dict[key][subkey] = config_dict
            else:
                config_dict = input(f"Enter value for {key}[{value or 'No default'}]: ") or value
                new_dict[key] = config_dict
        return new_dict


    def model_to_dict(self, config):
        if isinstance(config, GenericConfig) or isinstance(config, BaseModel):
            config_dict = config.model_dump()
        if isinstance(config, dict):
            env_dict = {}
            for key, value in config_dict.items():
                if isinstance(value, GenericConfig):
                    value = value.module_dump()
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        env_dict[f"{key}_{subkey}"] = subvalue
                else:
                    env_dict[key] = value
        return env_dict
    

    
    def model_to_yaml(self, config):
        if isinstance(config, GenericConfig) or isinstance(config, BaseModel):
            config_dict = self.model_to_dict(config)
        if config_dict:
            return yaml.dump(config_dict)
        
    def dict_to_env_lines(self, config_dict, args):
        self.lines = [f"{variable}\n" for variable in self._add_env(args)]
        lines = [f"{key}={value}\n" for key, value in config_dict.items()]
        lines.extend()
        return lines
    
    def write_environment(self, new_lines=None, file_path=None):
        if new_lines is None:
            new_lines = self._add_env(self.config)
        if not file_path:
            file_path = Path(f"module_validaotr/config/{__name__}.env")
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        new_lines.append(f"{os.getenv("MODULE_VALIDATOR_ENV")}={str(file_path)}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        load_dotenv(file_path)
        self.lines = new_lines
        return self.lines
    
    def dict_to_yaml(self, config):
        if isinstance(config, GenericConfig) or isinstance(config, BaseModel):
            config_dict = self.model_to_dict(config)
        if config_dict:
            return yaml.dump(config_dict)
    
    def load_bt_config(self, parser, args):
        self.bt_config = bt.config(parser, args)
        return self.bt_config

    
class bittensor_config(DefaultMunch):
    config: Configuration = Field(default_factory=Configuration)
    default = None
    lines: List[Any] = []
    bt_config = None
    parser = None
    args = None

    def __init__(self, parser=None, args=None, strict=False, default=None):
        super().__init__()
        if self.parser is None:
            self.parser = argparse.ArgumentParser(description="Bittensor Configuration")
        self.config = self.cli()
        self.parser = self._add_args(self.parser)
        self.args = sys.argv[1:] if args is None else args
        self.write_environment(self.config)
        self.config = bt.config(self.parser, args)
        if self.args:

            config_params = self.__parse_args__(args, parser, False)

            Load config from file if specified
            self._load_config_file(parser, args)

            Parse arguments again with potential new defaults
            params = self.__parse_args__(args, parser, config_params.strict or strict)

            Split params and add to config
            self.__split_params__(params, self.config)

            Track which parameters are set
            self._track_set_parameters(parser, args, params)
        self.config.config = bt.config(parser)



    def __str__(self):
        visible = copy.deepcopy(self.toDict())
        visible.pop("__parser", None)
        visible.pop("__is_set", None)
        return "\n" + yaml.dump(visible, sort_keys=False)

    def _add_args(self, parser: argparse.ArgumentParser):
        load_dotenv()
        parser.add_argument("--netuid", default=f"{os.getenv('netuid')}")
        return parser

    def _add_env_variables(self):
        self.lines = [
            f"netuid={self.config.netuid}",
        ]
        return self.lines

    def cli(self):
        load_dotenv()
        configure = input("Do you want to setup Bittensor configuration? (y/n) ")
        return Configuration(
            
        )

    @staticmethod
    def get_hotkey(wallet_name: str, hotkey_name: str):
        path = Path("~/.bittensor/wallets").expanduser()
        key_path = path / wallet_name / "hotkeys" / hotkey_name
        key_data = json.loads(key_path.read_text())
        public_key = key_data["publicKey"]
        private_key = key_data["privateKey"]
        ss58key = key_data["ss58Address"]
        return Keypair(ss58_address=ss58key, private_key=private_key, public_key=public_key)
        


def main():
    parser = argparse.ArgumentParser(description="bittensor configuration")
    return bittensor_config(parser=parser)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    configuration = bittensor_config(parser=parser)