import os
import argparse
import bittensor as bt
from pydantic import ConfigDict
from loguru import logger
from pydantic import BaseModel
from typing import Dict, Any, Union, Optional
from typing_extensions import Self
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bittensor.axon import FastAPIThreadedServer
from module_validator.chain.bittensor_subnet_template.docs.stream_tutorial.protocol import StreamingResponse, StreamPrompting
from module_validator.chain.bittensor_subnet_template.docs.stream_tutorial.config import get_config
from module_validator.chain.bittensor_subnet_template.docs.stream_tutorial.miner import StreamMiner
from dotenv import load_dotenv


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

load_dotenv()

config = get_config()


class WalletConfig(BaseModel):
    name: str
    hotkey: str
    path: str
    
    def get(self, name: str, default: str) -> str:
        return self.__getattr__(name or default)
    
    def __getattr__(self, name: str) -> Any:
        return super().__getattribute__(name)
    
    def __setattr__(self, name: Any, value: Any) -> None:
        super().__setattr__(name, value)


class AxonConfig(BaseModel):
    port: int
    ip: str
    external_ip: str
    external_port: int
    max_workers: int
    
    
class SubtensorConfig(BaseModel):
    network: str
    chain_endpoint: str
    _mock: bool
    
    
class MinerConfig(BaseModel):
    root: str
    name: str
    blocks_per_epoch: int
    no_serve: bool
    no_start_axon: bool
    mock_subtensor: bool
    full_path: str
    
    
class LoggingConfig(BaseModel):
    debug: bool
    trace: bool
    record_log: bool
    logging_dir: str
    
    
class Config(BaseModel):
    config: Dict[str, Any]
    
    
class Configuration(BaseModel):
    axon: AxonConfig
    subtensor: SubtensorConfig
    netuid: int
    miner: MinerConfig
    logging: LoggingConfig
    no_prompt: bool
    wallet: WalletConfig
    config: Union[Config, Dict[str, Any]]
    strict: bool
    no_version_checking: bool
    
    
class BittensorConfig(BaseModel):
    config: Optional[Union[Dict[str, Any], Configuration]]=None
    
    def __init__(self, **kwargs: Optional[Dict[str, Any]]) -> None:
        super().__init__(**kwargs)
        self.write_environment()
        self.config = self.add_args(parser=argparse.ArgumentParser())
        
    def cli(self, **kwargs: Optional[Dict[str, Any]]) -> Self:
        configure = input("Do you want to setup Bittensor configuration? (y/n) ")

        if kwargs:
            return Configuration(**kwargs)
        else:
            return (
                Configuration(
                    axon=AxonConfig(
                        port=8080,
                        ip=input("Enter axon ip[0.0.0.0]: ") or "0.0.0.0",
                        external_ip=input("Enter axon external ip[0.0.0.0]: ") or "0.0.0.0",
                        external_port=8080,
                        max_workers=input("Enter max workers[10]: ") or 10,
                    ),
                    subtensor=SubtensorConfig(
                        network=input(
                            "Enter subtensor network(finney/[testnet]/local): "
                        )
                        or "testnet",
                        chain_endpoint=input(
                            "Enter chain endpoint[wss://entrypoint-finney.opentensor.ai:443]: "
                        )
                        or "wss://entrypoint-finney.opentensor.ai:443",
                    ),
                    netuid=197,
                    miner=MinerConfig(
                        root=input(
                            "Enter miner root[/home/bakobi/.bittensor/miners/razor_test/]: "
                        )
                        or "/home/bakobi/.bittensor/miners/razor_test/",
                        name=input("Enter miner name[razor_hot]: ") or "razor_hot",
                        blocks_per_epoch=input("Enter blocks per epoch[100]: ") or 100,
                        no_serve=bool(input("Enter no_serve[False]: ")) or False,
                        no_start_axon=bool(input("Enter no_start_axon[False]: ")) or False,
                        mock_subtensor=bool(input("Enter mock_subtensor[False]: ")) or False,
                        full_path=input(
                            "Enter full_path[/home/bakobi/.bittensor/miners/razor_test/razor_hot/netuid197/razor_test]: "
                        ) or "/home/bakobi/.bittensor/miners/razor_test/razor_hot/netuid197/razor_test",
                    ),
                    logging=LoggingConfig(
                        debug=input("Enter debug[True]: ") or True,
                        trace=input("Enter trace[True]: ") or True,
                        record_log=input("Enter record_log[True]: ") or True,
                        logging_dir=input(
                            "Enter logging_dir[/home/bakobi/vscode/module_validator/.log]: "
                        )
                        or "/home/bakobi/vscode/module_validator/.log",
                    ),
                    no_prompt=False,
                    wallet=WalletConfig(
                        name=input("Enter wallet name[razor_test]: ") or "razor_test",
                        hotkey=input(
                            "Enter wallet hotkey[razor_hot]: "
                        )
                        or "razor_hot",
                        path=input(
                            "Enter wallet path[/home/bakobi/.bittensor/wallets]: "
                        )
                        or "/home/bakobi/.bittensor/wallets",
                    ),
                    config=input("Enter config[{}]: ") or {},
                    strict=input("Enter strict[False]: ") or False,
                    no_version_checking=input("Enter no_version_checking[False]: ")
                    or False,

                )
                if configure == "y"
                else Configuration(
                    axon=AxonConfig(
                        port=8080,
                        ip=os.getenv("axon_ip") or "0.0.0.0",
                        external_ip=os.getenv("axon_external_ip") or "0.0.0.0",
                        external_port=8080,
                        max_workers=int(os.getenv("axon_max_workers") or 8),
                    ),
                    subtensor=SubtensorConfig(
                        network=os.getenv("subtensor_network") or "testnet",
                        chain_endpoint=os.getenv("subtensor_chain_endpoint")
                        or "wss://entrypoint-finney.opentensor.ai:443",
                    ),
                    netuid=os.getenv("netuid") or 197,
                    miner=MinerConfig(
                        root=os.getenv("miner_root")
                        or "/home/bakobi/.bittensor/miners/razor_test/",
                        name=os.getenv("miner_name") or "razor_hot",
                        blocks_per_epoch=os.getenv("miner_blocks_per_epoch") or 100,
                        no_serve=os.getenv("miner_no_serve") or False,
                        no_start_axon=os.getenv("miner_no_start_axon") or False,
                        mock_subtensor=os.getenv("miner_mock_subtensor") or False,
                        full_path=os.getenv("full_path") or "/home/bakobi/.bittensor/miners/razor_test/razor_hot/netuid197/razor_test",

                    ),
                    logging=LoggingConfig(
                        debug=os.getenv("logging_debug") or True,
                        trace=os.getenv("logging_trace") or True,
                        record_log=os.getenv("logging_record_log") or True,
                        logging_dir=os.getenv("logging_logging_dir")
                        or "/home/bakobi/vscode/module_validator/.log",
                    ),
                    no_prompt=os.getenv("no_prompt") or False,
                    wallet=WalletConfig(
                        name=os.getenv("wallet_name") or "razor_test",
                        hotkey=os.getenv("wallet_hotkey") or "razor_hot",
                        path=os.getenv("wallet_path")
                        or "/home/bakobi/.bittensor/wallets",
                    ),
                    strict=os.getenv("strict") or False,
                    no_version_checking=os.getenv("no_version_checking") or False,
                    config=os.getenv("config") or {},
                )
            )
            
    def add_args(self, parser: argparse.ArgumentParser):
        parser.add_argument("--subtensor.network", default=f"{os.getenv('subtensor_network')}")
        parser.add_argument("--subtensor.chain_endpoint", default=f"{os.getenv('subtensor_chain_endpoint')}")
        parser.add_argument("--netuid", default=f"{os.getenv('netuid')}")
        parser.add_argument("--miner.name", default=f"{os.getenv('miner_name')}")
        parser.add_argument("--miner.blocks_per_epoch", default=f"{os.getenv('miner_blocks_per_epoch')}")
        parser.add_argument("--miner.no_serve", default=f"{os.getenv('miner_no_serve')}")
        parser.add_argument("--miner.no_start_axon", default=f"{os.getenv('miner_no_start_axon')}")
        parser.add_argument("--miner.mock_subtensor", default=f"{os.getenv('miner_mock_subtensor')}")
        parser.add_argument("--logger.debug", default=f"{os.getenv('logging_debug')}")
        parser.add_argument("--logger.trace", default=f"{os.getenv('logging_trace')}")
        parser.add_argument("--logger.record_log", default=f"{os.getenv('logging_record_log')}")
        parser.add_argument("--logger.logging_dir", default=f"{os.getenv('logging_logging_dir')}")
        parser.add_argument("--no_prompt", default=f"{os.getenv('no_prompt')}")
        parser.add_argument("--wallet.name", default=f"{os.getenv('wallet_name')}")
        parser.add_argument("--wallet.hotkey", default=f"{os.getenv('wallet_hotkey')}")
        parser.add_argument("--wallet.path", default=f"{os.getenv('wallet_path')}")
        parser.add_argument("--axon.port", default=f"{os.getenv('axon_port')}")
        parser.add_argument("--axon.ip", default=f"{os.getenv('axon_ip')}")
        parser.add_argument("--axon.external_port", default=f"{os.getenv('axon_port')}")
        parser.add_argument("--axon.external_ip", default=f"{os.getenv('axon_external_ip')}")
        parser.add_argument("--axon.max_workers", default=f"{os.getenv('axon_max_workers')}")
        parser.add_argument("--miner.full_path", default=f"{os.getenv('miner_full_path')}")

    def write_environment(self):
        logger.info("Writing .env file...")
        settings = self.cli()
        logger.debug(settings)

        settings_dict = {}
        if isinstance(settings, BaseModel):
            settings_dict = settings.model_dump()

        env_dict = {}

        for key, value in settings_dict.items():
            if isinstance(value, BaseModel):
                value = value.model_dump()
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    env_dict[f"{key}_{subkey}"] = subvalue
            else:
                env_dict[key] = value

        lines = [f"{key} = {value}\n" for key, value in env_dict.items()]
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(lines)
        return settings_dict


if __name__ == "__main__":
    bit = BittensorConfig()
    print(bit.config)
    print(os.environ)
    