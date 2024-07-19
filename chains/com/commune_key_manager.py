import json
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, Any, Optional
from pathlib import Path
from base.base_miner import MinerConfig
from substrateinterface import Keypair
from communex._common import get_node_url
from communex.client import CommuneClient
from dotenv import load_dotenv


load_dotenv()

comx = CommuneClient(get_node_url())


class KeyManager(ABC):
    @abstractmethod
    def add_miner_key(
        self,
        key_name: str,
        miner_keypath: Path,
        miner_config: Optional[MinerConfig] = None,
    ):
        """Add a new miner key for the given key_name."""

    @abstractmethod
    def remove_miner_key(self, key_name: str, miner_keypath: Path):
        """Remove the miner key for the given key_name."""

    @abstractmethod
    def update_miner_key(
        self, key_name: str, miner_config: MinerConfig, miner_keypath: Path
    ):
        """Update the miner key for the given key_name."""

    @abstractmethod
    def _save_miner_keys(self, miner_keypath: Path):
        """Save the miner keys to the given miner_keypath."""

    @abstractmethod
    def get_miner_keys(self, key_name: str) -> Dict[str, Any]:
        """Get the miner keys for the given key_name."""

    @abstractmethod
    def register_miner(self, miner_config: MinerConfig) -> None:
        """Register a new miner on the blockchain."""


class CommuneKeyManager(BaseModel, KeyManager):
    keyring: Dict[str, Any]
    miner_config: MinerConfig
    miner_configs: Dict[str, MinerConfig]
    miner_key_name: str
    miner_key_path: str
    miner_endpoint: str
    miner_url: str

    def __init__(
        self,
        keyring: Dict[str, Any],
        miner_config: MinerConfig,
        miner_configs: Dict[str, MinerConfig],
        miner_key_name: str,
        miner_key_path: str,
        miner_endpoint: str,
        miner_url: str,
    ):
        self.keyring = keyring
        self.miner_config = miner_config
        self.miner_configs = miner_configs
        self.miner_key_name = miner_key_name
        self.miner_key_path = miner_key_path
        self.miner_endpoint = miner_endpoint
        self.miner_url = miner_url

    def add_miner_key(
        self,
        key_name: str,
        miner_keypath: Path,
        miner_config: Optional[MinerConfig] = None,
    ):
        with open(f"$HOME/.commune/{key_name}.json", "r") as f:
            json_data = json.loads(f.read())["data"]
            keypair = Keypair.from_uri(json_data)
            keyring = self.keyring
            keyring[key_name] = keypair
            self.keyring = keyring
            self.miner_config = miner_config
            self.miner_configs[key_name] = miner_config
            self._save_miner_keys(miner_keypath)

    def _save_miner_keys(self, miner_keypath: Path):
        with open(miner_keypath, "w") as f:
            f.write(json.dumps(self.miner_configs, indent=4))

    def _update_miner_key(
        self, key_name: str, miner_config: MinerConfig, miner_keypath: Path
    ) -> None:
        self.add_miner_key(key_name, miner_keypath, miner_config)
        self._save_miner_keys(miner_keypath)

    def get_miner_keys(self) -> Dict[str, Any]:
        return self.keyring

    def get_miner_key(self, key_name: str) -> Any:
        return self.keyring[key_name]

    def remove_miner_key(self, key_name: str, miner_keypath: Path):
        del self.keyring[key_name]
        del self.miner_configs[key_name]
        self._save_miner_keys(miner_keypath)

    def register_miner(self, miner_config: MinerConfig) -> None:
        return super().register_miner(miner_config)
