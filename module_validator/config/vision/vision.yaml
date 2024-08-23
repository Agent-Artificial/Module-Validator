from pydantic import BaseModel, Field
from typing import Any
from dotenv import load_dotenv
import os

load_dotenv()





class Config(GenericConfig):
    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
    env_file: Any = Field(default=None)
    default_axon_external_ip: Any = Field(default=None)
    default_axon_external_port: Any = Field(default=None)
    axon_port: Any = Field(default=None)
    subtensor_network: Any = Field(default=None)
    axon_external_ip: Any = Field(default=None)
    default_axon_max_workers: Any = Field(default=None)
    default_axon_ip: Any = Field(default=None)
    debug_miner: Any = Field(default=None)
    netuid: Any = Field(default=None)
    wallet_name: Any = Field(default=None)
    subtensor_chain_endpoint: Any = Field(default=None)
    default_axon_port: Any = Field(default=None)
    wallet_hotkey: Any = Field(default=None)



    env_file: Any = Field(default=None)
    default_axon_external_ip: Any = Field(default=None)
    default_axon_external_port: Any = Field(default=None)
    axon_port: Any = Field(default=None)
    subtensor_network: Any = Field(default=None)
    axon_external_ip: Any = Field(default=None)
    default_axon_max_workers: Any = Field(default=None)
    default_axon_ip: Any = Field(default=None)
    debug_miner: Any = Field(default=None)
    netuid: Any = Field(default=None)
    wallet_name: Any = Field(default=None)
    subtensor_chain_endpoint: Any = Field(default=None)
    default_axon_port: Any = Field(default=None)
    wallet_hotkey: Any = Field(default=None)

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
