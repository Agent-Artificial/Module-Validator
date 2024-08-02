import requests
import subprocess
import uvicorn
import json
import os
from pydantic import BaseModel
from substrateinterface import ExtrinsicReceipt
from abc import ABC, abstractmethod
from importlib import import_module
from multiprocessing import Pool, process
from typing import Any, Dict, List, Optional, Tuple, Union
from base.base_module import BaseModule, ModuleConfig
from data_models import MinerRequest
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.api import serve_spa

from dotenv import load_dotenv

load_dotenv()
    
    
class ValidatorRequest(BaseModel):
    data: Optional[Any] = None
    

class ValidatorSettings(BaseModel):
    validator_name: Optional[str] = None
    validator_keypath: Optional[str] = None
    validator_port: Optional[str] = None
    validator_host: Optional[str] = None
    use_testnet: Optional[bool] = None
    netuid: Optional[int] = None
    stake: Optional[float] = None
    funding_key: Optional[str] = None
    modifier: Optional[float] = None
    inference_url: Optional[str] = None
    inference_api_key: Optional[str] = None


class ValidatorExecutor:
    chain_api: Optional[Dict[str, Any]]
    module_registry: Optional[Dict[str, Any]]
    module_config: Optional[Dict[str, Any]]
    validator_config: Optional[Union[ValidatorSettings, Dict[str, Any]]]
    module: Optional[BaseModule]
    Validator_statistics: Optional[Dict[str, Any]]
    
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
        module_name: str = "embedding",
        module_endpoint: str = "/modules/embedding",
        module_path: str = "modules/embedding",
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
    
    def construct_validator_request(self, sample_data: Any) -> ValidatorRequest:
        return ValidatorRequest(data={**sample_data})
        
    def process_sample_data(self, sample_data: str):
        request = self.construct_validator_request(sample_data)
        return self.module.process(request)
        
    @abstractmethod
    def collect_miner_addresses(self) -> Tuple[List[int], List[str]]:
        """returns a tuple of (validator_uids, validator_addresses)"""
        
    @abstractmethod
    def validate(self, sample_data: Any, request: ValidatorRequest, validators: List[str]) -> Tuple[int, List[float]]:
        """returns a tuple of (validator_uid, result_tensors)"""
        
    @abstractmethod
    def normalize(self, results: List[float]) -> List[float]:
        """returns a tuple of (validator_uids, normalized_results)"""
        
    @abstractmethod
    def scale(self, normalized_results: List[float]) -> List[float]:
        """returns a list of scaled results"""
        
    @abstractmethod
    def vote(self, validator_uids: List[int], scaled_results: List[float], validator_addresses: List[str]) -> Any:
        """votes on the chain, returns the receipt"""

    @abstractmethod
    def voteloop(self, validator_uids: List[int], scaled_results: List[float], validator_addresses: List[str]) -> Any:
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
        def miner_statistics():
            validator_uids, validator_addresses = self.collect_miner_addresses()
            return {"miners_uids": validator_uids, "miner_addresses": validator_addresses}
        
        @app.post("/validate")
        def validate(sample_data: str, request: MinerRequest, validator_addresses: List[str]):
            result = self.validate(sample_data, request, validator_addresses)
            return {"results": result}
            
        uvicorn.run(app, host=os.getenv("VALIDATOR_HOST"), port=os.getenv("VALIDATOR_PORT"), reload=True)