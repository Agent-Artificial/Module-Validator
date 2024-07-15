import requests
import subprocess
import uvicorn
import json
import os
from substrateinterface import ExtrinsicReceipt
from abc import ABC, abstractmethod
from importlib import import_module
from multiprocessing import Pool, process
from typing import Any, Dict, List, Optional, Tuple
from data_models import MinerRequest, ValidatorSettings
from base.base_module import BaseModule, ModuleConfig
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.api import serve_spa

from dotenv import load_dotenv

load_dotenv()


class ValdiatorExecutor:
    chain_api: Optional[Dict[str, Any]]
    module_registry: Optional[Dict[str, Any]]
    module_config: Optional[Dict[str, Any]]
    validator_config: ValidatorSettings
    module: Optional[BaseModule]
    miner_statistics: Optional[Dict[str, Any]]
    
    def __init__(
        self, 
        validator_config: ValidatorSettings,
    ):
        self.validator_config = validator_config
        self.module_config = self.set_module_config()
        self.module_registry = self.get_module_registry(self.module_config.module_url)
        self.chain_api = self.init_chain_api()
        if self.module_config.module_name not in os.listdir("modules"):
            self.install_module(self.module_config)
        
        self.module = self.get_module(self.module_config)
        self.process = self.module.process
        self.miner_statistics = {}
        
    def set_module_config(
        self,
        module_name: str = "translation",
        module_endpoint: str = "/modules/translation",
        module_path: str = "modules/translation",
        module_url: str = "https://registrar-cellium.ngrok.app/"
    ):
        return ModuleConfig(
            module_name=module_name,
            module_endpoint=module_endpoint,
            module_path=module_path,
            module_url=module_url
        )
        
    def get_module_registry(self, module_url: str):
        url = f"{module_url}/modules/registry"
        response = requests.get(url, timeout=30)
        with open("data/registry.json", "w", encoding="utf-8") as f:
            json.dumps(f.write(json.dumps(response.json())), indent=4)
        return response.content
        
    async def init_chain_api(self):
        await serve_spa()
        return "https://comx-cellium.ngrok.app/comx"

    def install_module(self, module_config: ModuleConfig):
        module_config = module_config or self.module_config
        base_module = BaseModule(module_config)
        base_module.install_module(module_config)
    
    def get_module(self, module_config: ModuleConfig):
        module = import_module(f"modules.{module_config.module_name}.{module_config.module_name}")
        module = getattr(module, f"{module_config.module_name.title()}")
        return module
    
    def construct_miner_request(self, sample_data: Any, request: MinerRequest) -> MinerRequest:
        request_dict = request.model_dump()
        return MinerRequest(data={"request_data": sample_data, **request_dict})
        
    def process_sample_data(self, sample_data: str, request: MinerRequest):
        miner_request = self.construct_miner_request(sample_data, request)
        return self.module.process(miner_request)
        
    @abstractmethod
    def collect_miner_addresses(self) -> Tuple[List[int], List[str]]:
        """returns a tuple of (miner_uids, miner_addresses)"""
        
    @abstractmethod
    def validate(self, sample_data: Any, request: MinerRequest, miners: List[str]) -> Tuple[int, List[float]]:
        """returns a tuple of (miner_uid, result_tensors)"""
        
    @abstractmethod
    def normalize(self, results: List[float]) -> List[float]:
        """returns a tuple of (miner_uids, normalized_results)"""
        
    @abstractmethod
    def scale(self, normalized_results: List[float]) -> List[float]:
        """returns a list of scaled results"""
        
    @abstractmethod
    def vote(self, miner_uids: List[int], scaled_results: List[float], miner_addresses: List[str]) -> Any:
        """votes on the chain, returns the receipt"""

    @abstractmethod
    def voteloop(self, miner_uids: List[int], scaled_results: List[float], miner_addresses: List[str]) -> Any:
        """main voting loop""" 
        
    def serve(self):
        app = FastAPI()
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        def health():
            return {"status": "healthy"}
        
        @app.get("/miners")
        def miners():
            miner_uids, miner_addresses = self.collect_miner_addresses()
            return {"miner_uids": miner_uids, "miner_addresses": miner_addresses}
        
        @app.get("/stats")
        def stats():
            return self.miner_statistics
            
        uvicorn.run(app, host="0.0.0.0", port=6767, reload=True)