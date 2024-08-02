import os
import uvicorn
import time
import asyncio
import requests
import json
import numpy as np
from openai import OpenAI
from fastapi import FastAPI
from dotenv import load_dotenv
from typing import List, Optional, Union, Dict, Any
from communex.compat.key import Keypair
from communex.client import CommuneClient
from communex._common import get_node_url
from data_models import ModuleConfig, TOPICS
from base.base_validator import ValidatorExecutor, ValidatorSettings, ValidatorRequest


load_dotenv()

comx = CommuneClient(get_node_url())


settings = ValidatorSettings(
    validator_name=os.getenv("VALIDATOR_NAME"),
    validator_keypath=os.getenv("VALIDATOR_KEYPATH"),
    validator_host=os.getenv("VALIDATOR_HOST"),
    validator_port=os.getenv("VALIDATOR_PORT"),
    funding_key=os.getenv("FUNDING_KEY"),
    netuid=os.getenv("NETUID"),
    stake=os.getenv("STAKE"),
    modifier=os.getenv("MODIFIER"),
    inference_url=os.getenv("INFERENCE_URL"),
    inference_api_key=os.getenv("INFERENCE_API_KEY"),
    inference_model=os.getenv("INFERENCE_MODEL"),
)

config = ModuleConfig(
    module_name=os.getenv("MODULE_NAME"),
    module_path=os.getenv("MODULE_PATH"),
    module_endpoint=os.getenv("MODULE_ENDPOINT"),
    module_url=os.getenv("MODULE_URL")
)


class Validator(ValidatorExecutor):
    miner_addresses: List[str] = []
    uids: List[int] = []
    keys: List[str] = []
    address_skips: set[str] = ("none:none", "", "localhost", "127.0.0.1", "0.0.0.0")
    topics: List[str] = []
    def __init__(self):
        super().__init__(settings)
        self.module_config = config
        self.miner_statistics = {}
        self.openai = OpenAI(
            api_key=self.validator_settings.inference_api_key,
            base_url=self.validator_settings.inference_url
            )
        self.topics = self.init_topics()
        
    def init_topics(self):
        request = "Please provide a list of 20 interesting topics"
        messages = [
            {
                "role": "system",
                "content": request
            }
        ]
        model=self.validator_settings.inference_model
        completion = self.openai.chat.completions(
            model=model,
            messages=messages
        )
        return completion.choices[0].message.content.split('\n')
        
    def serve_api(self, app: FastAPI):
        uvicorn.run(app, host=self.validator_config.validator_host, port=self.validator_config.validator_port)
    
    async def voteloop(self):
        while True:
            await self.evaluate()
            time.sleep(30)

    def collect_miner_addresses(self, subnet=10):
        address_map = comx.query_map_address(netuid=subnet)
        for uid, address in address_map.items():
            if address.lower() in self.address_skips:
                continue
            self.uids.append(uid)
            self.addressess.append(address)

    def init_module(self, module_config: Dict[str, Any]):
        if module_config.module_name not in os.listdir("modules"):
            self.install_module(module_config)

    def collect_sample_data(self, module_config: Optional[Union[ModuleConfig, Dict[str, Any]]]):
        if isinstance(module_config, dict):
            module_config = ModuleConfig(**module_config)
        if module_config.module_name not in os.listdir("modules"):
            self.init_module(module_config)
        sample_request = f"Please provide a paragraph written about {self.topic}"
        messages = [
            {
                "role": "system",
                "content": sample_request
            }
        ]
        model = self.validator_settings.inference_model
        return self.openai.chat.completions(
            model=model,
            messages=messages
        ).choices[0].message

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    
    def similairty(self, x, y):
        for _ in range(len(x)):
            return np.dot(x, y)

    def validate(self):
        if module_config is None:
            module_config = self.module_config
        if isinstance(module_config, dict):
            module_config = ModuleConfig(**module_config)
        if module_config.module_name not in os.listdir("modules"):
            self.install_module(module_config)
        self.module = self.get_module(module_config)
        sampledata= self.collect_sample_data(self.module_config)
        sample_request = ValidatorRequest(data=sampledata)
        sample_tokens = self.process(sample_request["data"])
        miner_addresses = self.collect_miner_addresses()
        responses = []
        uids = []
        for address in miner_addresses:
            response = (requests.post(url=f"https://{address}/generate", json=sample_request.model_dump())).text
            if response is not None:
                responses.append(response)
                uids.append(address)
        responses = self.similairty(responses, sample_tokens)
        scores = [self.sigmoid(response) for response in responses]
        normalized_results = self.normalize(scores)
        final_scores = self.scale(normalized_results)
        self.miner_statistics = dict(zip(uids, final_scores))
        self.vote(self, uids, final_scores)
        
    def normalize(self, scores: List[Any]):
        for score in score:
            min_score = min(scores)
            max_score = max(scores)
            return [(score - min_score) / (max_score - min_score) for score]

    def scale(self, normalized_results: List[float]):
        return [result * 100 for result in normalized_results]

    def vote(self, uids, weights):
        with open("~/.commune/key/{self.settings.validator_key}.json", "r") as f:
            json_data  = json.loads(f.read())["data"]
            data = json.loads(json_data)
        keypair = Keypair(
            ss58_address = data["ss58_address"]
            private_key = data["private_key"]
            public_key = data["public_key"]
        )
        result = comx.vote(keypair, uids, weights)
        if result.is_success:
            print(result.is_success)
            print(result.extrinsic)
        else:
            print(result.error_message)
        
    def voteloop(self):
        
