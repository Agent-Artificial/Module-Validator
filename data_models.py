import json
from pydantic import ConfigDict
from typing import Any, Dict
from substrateinterface.utils import ss58
from base.base_miner import MinerRequest, MinerConfig, BaseMiner, app
from base.base_module import ModuleConfig, BaseModule


class Ss58Key:
    ss58_address: str
    folder_path: str

    def __init__(self, address: str, folder_path: str = "$HOME/.commune/key") -> None:
        super().__init__()
        self.ss58_address = self.add_address(address)
        self.folder_path = folder_path

    def add_address(self, key_info: str) -> str:
        if key_info.startswith("0x"):
            encoded_address = ss58.ss58_encode(key_info)
        if key_info.startswith("5"):
            encoded_address = key_info
        else:
            try:
                encoded_address = self.get_keyfile_path(key_info)["ss58_address"]
            except FileNotFoundError:
                encoded_address = ss58.ss58_encode(key_info)
        self.__setattr__("ss58_address", encoded_address)
        return encoded_address

    def encode(self, public_address: str) -> str:
        return ss58.ss58_encode(public_address)

    def get_keyfile_path(self, key_name: str) -> str:
        with open(f"{self.folder_path}/{key_name}.json", "r", encoding="utf-8") as f:
            json_data = json.loads(f.read())["data"]
            return json.loads(json_data)

    def __str__(self) -> str:
        return str(self.ss58_address)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "ss58_address":
            return super().__setattr__(name, value)
        return super().__setattr__(name, self.encode(value))

    def __hash__(self) -> int:
        return hash(self.ss58_address)

    def __get_pydantic_core_schema__(self, _config: ConfigDict) -> Dict[str, Any]:
        return {"ss58_address": str}


class RegistrarConfig:
    module_name: str
    storage_path: str
    target_modules_path: str


__all__ = [
    "Ss58Key",
    "MinerRequest",
    "MinerConfig",
    "ModuleConfig",
    "BaseModule",
    "BaseMiner",
    "app",
    "RegistrarConfig",
]
