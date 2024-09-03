import json
import argparse
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Union, TypeVar, List, Optional
import bittensor as bt
from bittensor.metagraph import TorchMetaGraph, NonTorchMetagraph

T = TypeVar("T")
bt.metagraph

class GenericConfig(BaseModel):
    file: Optional[str] = Field(default_factory=str, type=str)
    hotkey: Optional[str] = Field(default_factory=str, type=str)
    message: Optional[Dict[str, Any]] = Field(default_factory=dict, type=dict)
    miner: Optional[bt.axon] = Field(default_factory = bt.axon, type=bt.axon)
    mock: Optional[bool] = Field(defaul=True, type=bool)
    my_uid: Optional[int] = Field(default_factory=int, type=int)
    netuid: Optional[int] = Field(default_factory=int, type=int)
    network: Optional[str] = Field(default_factory=str, type=str)
    neuron: Optional[Dict[str, Any]] = Field(default_factory=dict, type=dict)
    wallet_name = Optional[str] = Field(default_factory=str, type=str)
    wandb: Optional[Dict[str, Any]] = Field(default_factory=dict, type=dict)
    hotkeypair: Optional[bt.Keypair] = Field(default_factory=bt.Keypair, type=None)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, type=None)
    axon: Optional[bt.axon] = Field(default_factory=bt.axon, type=None)
    wallet: Optional[bt.wallet] = Field(default_factory=bt.wallet, type=None)
    metagraph: Optional[Union[type[TorchMetaGraph], type[NonTorchMetagraph]]] = Field(default_factory=Union[TorchMetaGraph, NonTorchMetagraph], type=None)
    subtensor: Optional[bt.subtensor] = Field(default_factory=bt.subtensor, type=None)
    dendrite: Optional[bt.dendrite] = Field(default_factory=bt.dendrite, type=None)
    hotkeypair: Optional[bt.Keypair] = Field(default_factory=bt.Keypair, type=None)
    model_config: ConfigDict = ConfigDict({
        "arbitrary_types_allowed": True
    })
    __pydantic_fields_set__ = set([
        "file",
        "hotkey",
        "message",
        "miner",
        "mock",
        "my_uid",
        "netuid",
        "network",
        "neuron",
        "wallet_name",
        "wandb",
        "hotkeypair",
        "config",
        "axon",
        "wallet",
        "metagraph",
        "subtensor",
        "dendrite",
        "hotkeypair"
    ])

    def __init__(self, data: Dict[str, Any]=None):
        super(BaseModel).__init__()
        self.config = {}
        config_data = self.config or data
        self.config = self._merge(config_data, self.config) if self.config else config_data
        

    @classmethod
    def _get(cls, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = cls.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @classmethod
    def _set(cls, key: str, value: Any):
        keys = key.split(".")
        d = cls.config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    @classmethod
    def _merge(
        cls, new_config: Dict[str, Any], old_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        merged_config = old_config.copy()
        for key, value in new_config.items():
            if (
                isinstance(value, dict)
                and key in merged_config
                and isinstance(merged_config[key], dict)
            ):
                merged_config[key] = cls._merge(value, merged_config[key])
            else:
                merged_config[key] = value
        return merged_config

    @classmethod
    def _load_config(
        cls, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> "GenericConfig":
        config = cls(config={})
        config._parse_args(args)
        return config

    @classmethod
    def _parse_args(cls, args: argparse.Namespace):
        for arg, value in vars(args).items():
            if value is not None:
                cls._set(arg, value)

    @classmethod
    def _prompt_for_value(cls, key: str, default: Any = None) -> Any:
        if key in cls._config:
            value = input(f"Enter value for {key}[{default}]: ")
            cls.__set(key, value)
            return value

if __name__ == "__main__":

    config = GenericConfig(config={})
