import os
from bittensor.config import config
from dotenv import load_dotenv


def get_config():
    return {
        "netuid": 1,
        "subtensor": {"network": "local", "chain_endpoint": "ws://127.0.0.1:9946" , "_mock": False},
        "pow_register": {
            "num_processes": None,
            "update_interval": 50000,
            "output_in_place": True,
            "verbose": False,
            "cuda": {"dev_id": [0], "use_cuda": True, "tpb": 256},
        },
        "axon": {
            "port": 4267,
            "ip": "[::]",
            "external_port": None,
            "external_ip": None,
            "max_workers": 10,
            "maximum_concurrent_rpcs": 400,
        },
        "priority": {"max_workers": 5, "maxsize": 10},
        "prometheus": {"port": 7091, "level": "INFO"},
        "wallet": {
            "name": os.getenv("MINER_COLD_KEY"),
            "hotkey": os.getenv("MINER_HOT_KEY"),
            "path": "~/.bittensor/wallets/",
        },
        "dataset": {
            "batch_size": 10,
            "block_size": 20,
            "num_workers": 0,
            "dataset_names": "default",
            "data_dir": "~/.bittensor/data/",
            "save_dataset": False,
            "max_datasets": 3,
            "num_batches": 100,
        },
        "logging": {
            "debug": False,
            "trace": False,
            "record_log": False,
            "logging_dir": "~/.bittensor/miners",
        },
    }
