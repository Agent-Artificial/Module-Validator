import os
import json
import requests
import base64
from requests import Response, Request
from typing import List, Dict, Tuple, Any, Optional
from base.base_module import BaseModule, ModuleConfig
from base.base_validator import ValdiatorExecutor, ValidatorSettings
from data_models import MinerRequest, CLIENT_FILES
from load_dotenv import load_dotenv


load_dotenv()


validator_config = ValidatorSettings(
    name=os.getenv("VALIDATOR_NAME"),
    ss58_address=os.getenv("VALIDATOR_SS58KEY"),
    keypath=os.getenv("KEY_FOLDER"),
    keyname=os.getenv("VALIDATOR_KEYNAME"),
    host_address=os.getenv("VALIDATOR_HOST"),
    external_address=os.getenv("VALIDATOR_EXTERNAL_ADDRESS"),
    port=os.getenv("VALIDATOR_PORT"),
    chain="commune",
    use_testnet=False,
    subnet_list=[10, 0]
)

module_config = ModuleConfig(
    module_name="translation",
    module_endpoint="/modules/translation",
    module_url="https://registrar-cellium.ngrok.app/",
    module_path="modules/translation"
)


class CommuneValidator(ValdiatorExecutor):
    def __init__(self, validator_config: ValidatorSettings):
        super().__init__(validator_config)
        self.validator_config = validator_config
        self.module_config = module_config
        self.module = self.get_module(self.module_config)
        self.miner_statistics = {}
      
    def collect_miner_addresses(self) -> Tuple[List[int], List[str]]:
        url = f"{self.chain_api}/comx/query_map_addresses?subnet=10"
        result = requests.get(url, timeout=30)
        print(result.json())
        
    def validate(self, sample_data: Any, request: MinerRequest, miners: List[str]) -> Tuple[int, List[float]]:
        sample_data = 
    request_path = "modules/translation/in/request.txt"
    with open(request_path, "w", encoding="utf-8") as f:
        json.dumps(f.write(sample_data))
    
    module = validator.get_module(module_config)()
    data = module.process(
        in_file="modules/translation/in/request.txt",
        task_string="text2speech",
        target_languages=["French"]
    )
    
    with open("modules/translation/out/test_output.txt", "wb") as f:
        f.write(data[1])
        
    def normalize(self, results: List[float]) -> List[float]:
        """returns a tuple of (miner_uids, normalized_results)"""
        pass
        
    def scale(self, normalized_results: List[float]) -> List[float]:
        """returns a list of scaled results"""
        pass
        
    def vote(self, miner_uids: List[int], scaled_results: List[float], miner_addresses: List[str]) -> Any:
        """votes on the chain, returns the receipt"""
        pass

    def voteloop(self, miner_uids: List[int], scaled_results: List[float], miner_addresses: List[str]) -> Any:
        """main voting loop""" 
        pass
        
        
if __name__ == "__main__":
