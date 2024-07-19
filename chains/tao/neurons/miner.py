import os
import uvicorn
import subprocess
from importlib import import_module
from fastapi import FastAPI
from typing import List, Callable, Optional
from chains.tao.neurons.config import get_config
from data_models import BaseModule, MinerRequest, ModuleConfig



class TAOMiner():
    def __init__(self,  module_config: ModuleConfig):
        super().__init__()
        self.config = get_config()
        self.module_config = module_config
        self.process = None
        self.module = None
        
    def set_module(self, module_config: ModuleConfig):
        module = import_module(f"{module_config.module_path.replace('/', '.')}.{module_config.module_name}")
        module = getattr(module, module_config.module_name.title())
        self.module = module()
        
    async def forward(self, miner_request: MinerRequest):
        return self.module.process(self.module, miner_request=miner_request)
    
    def set_process(self, process: Callable):
        self.process = process
        
    def register_miner(self, command: Optional[str] = "register", wallet_name: Optional[str] = "miner", hotkey: Optional[str] = "default"):
        command = ["btcli", "subnet", f"{command}", "--wallet.name", f'{wallet_name}', "--wallet.hotkey", f'{hotkey}', "--subtensor.chain_endpoint", "ws://127.0.0.1:9946"]
        subprocess.run(command, check=True)
        
    def serve_miner(self, app: FastAPI):
        uvicorn.run(app, host="0.0.0.0", port=4270)
        