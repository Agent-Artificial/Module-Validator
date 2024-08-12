import os
from scipy import spatial
import uvicorn
import time
import asyncio
import requests
import json
import random
import aiohttp
import numpy as np
from openai import OpenAI
from fastapi import FastAPI
from dotenv import load_dotenv
from typing import List, Optional, Union, Dict, Any
from communex.compat.key import Keypair
from communex.client import CommuneClient
from communex._common import get_node_url
from data_models import ModuleConfig
from base.base_validator import ValidatorExecutor, ValidatorSettings, ValidatorRequest
from validators.config import use_default_config
from loguru import logger
from chains.com.get_miner_data import get_miner_uids

load_dotenv()

comx = CommuneClient(get_node_url())

use_default_config()


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
    module_url=os.getenv("MODULE_URL"),
)

openai = OpenAI(api_key=settings.inference_api_key, base_url=settings.inference_url)


class Validator(ValidatorExecutor):
    logger.info("Starting Validator")
    addresses: List[str] = []
    uids: List[int] = []
    keys: List[str] = []
    address_skips: set[str] = ("none:none", "", "localhost", "127.0.0.1", "0.0.0.0")
    topics: List[str] = []
    miner_statistics: Dict[str, Any] = {}
    weights: List[float] = []
    scores: List[float] = []
    miner_info: Dict[str, Any] = {}
    subnets = [3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17]
    

    def __init__(self):
        super().__init__(settings)
        self.module_config = config
        self.init_module(self.module_config)
        self.topics = self.init_topics()
        self.miner_statistics = {}
        
    def clear(self):
        self.uids = []
        self.keys = []
        self.weights = []
        self.scores = []
        self.addresses = []

    def init_topics(self):
        logger.info("Initializing topics")
        request = "Please provide a list of 20 interesting topics"
        messages = [{"role": "system", "content": request}]
        model = settings.inference_model
        completion = openai.chat.completions.create(messages=messages, model=model)

        return completion.choices[0].message.content.split("**")

    def serve_api(self, app: FastAPI):
        logger.info("Serving API")
        uvicorn.run(
            app,
            host=self.validator_config.validator_host,
            port=self.validator_config.validator_port,
        )

    async def voteloop(self):
        logger.info("Starting Voteloop")
        self.module = self.module()
        while True:
            for subnet in self.subnets:
                self.miner_info = get_miner_uids(key_dict=self.miner_info)
        
                await self.validate(self.module_config, subnet=subnet)
            time.sleep(30)

    def collect_miner_addresses(self, subnet=10):
        logger.info("Collecting miner addresses")
        address_map = comx.query_map_address(netuid=subnet)
        uids = []
        for uid, address in address_map.items():
            if address.lower() in self.address_skips:
                continue
            self.addresses.append(address)
            uids.append(uid)

        return self.addresses, uids
    
    def init_module(self, module_config: Dict[str, Any]):
        logger.info("Initializing module")
        if module_config.module_name not in os.listdir("modules"):
            self.install_module(module_config)

    def collect_sample_data(
        self, module_config: Optional[Union[ModuleConfig, Dict[str, Any]]]
    ):
        logger.info("Collecting sample data")
        if isinstance(module_config, dict):
            module_config = ModuleConfig(**module_config)
        if module_config.module_name not in os.listdir("modules"):
            self.init_module(module_config)
        sample_request = (
            f"Please provide a paragraph written about {random.choice(self.topics)}"
        )
        messages = [{"role": "system", "content": sample_request}]
        model = settings.inference_model
        return (
            openai.chat.completions.create(model=model, messages=messages)
            .choices[0]
            .message.content
        )

    def sigmoid(self, x):
        logger.info("Performing sigmoid")
        return 1 / (1 + np.exp(-x))

    def similairty(self, x, y):
        logger.info("Performing similairty")
        return self.sigmoid(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y)))

    async def validate(self, module_config: Optional[Dict[str, Any]], subnet=10):
        logger.info("Validating")
        
        if module_config is None:
            module_config = self.module_config
        if isinstance(module_config, dict):
            module_config = ModuleConfig(**module_config)
        if module_config.module_name not in os.listdir("modules"):
            self.install_module(module_config)
        
        responses = await self.async_miner_responses(addresses=miner_addresses, miner_request=sample_messages)
        with open("modules.json", "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            for miner in data.values():
                miner_name = miner["name"]
                miner_key = miner["key"]
                
                for key in self.keys:
                    if key == vali_key:
                        continue
        for j, response in enumerate(responses):
            if response is None or response == "None" or response == "":
                score = 0.1
            else:
                response = json.loads(response)["choices"][0]["message"]["content"]
                logger.debug(response)
                score = self.similairty(response, sample_tokens)
            if miner_uids[j] == 82:
                continue
            if miner_uids[j] in mineruids:
                score = 0.731
            self.uids.append(miner_uids[j])
            self.weights.append(score * 10)
            logger.debug(score)
        self.miner_statistics = dict(zip(self.uids, self.weights))
        with open("static/miner_statistics.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.miner_statistics, indent=4))
        print(len(self.uids), len(self.weights))
        result = self.vote(self.uids, self.weights)
        logger.debug(result)

    def normalize(self, scores: List[Any]):
        logger.info("Normalizing")
        for _ in scores:
            min_score = min(scores)
            max_score = max(scores)
            return [(score - min_score) / (max_score - min_score) for score in scores if score != 0] or 0.1

    def vote(self, uids, weights):
        logger.info("Voting")
        with open("/home/bakobi/.commune/key/eden.Validator.json", "r", encoding="utf-8") as f:
            json_data = json.loads(f.read())["data"]
            data = json.loads(json_data)
        keypair = Keypair(
            ss58_address=data["ss58_address"],
            private_key=data["private_key"],
            public_key=data["public_key"],
        )
        print(uids)
        print(weights)
        logger.debug(uids)
        logger.debug(weights)
        print(len(self.uids), len(self.weights))
        result = comx.vote(keypair, self.uids, self.weights, netuid=10)
        self.clear()
        if result.is_success:
            print(result.is_success)
            print(result.extrinsic)
        else:
            print(result.error_message)
        return result

    async def fetch_miner_responses(self, http_client, miner_request, url):
        try:
            async with http_client.post(f"http://{url}/generate", json=miner_request, timeout=10) as response:
                if response.status != 200:
                    response.raise_for_status()
                return await response.text()
        except Exception as e:
            print(f"Error requesting module: {e}")
    
    async def fetch_all(self, http_client, miner_request, urls):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self.fetch_miner_responses(http_client, miner_request, url))
            tasks.append(task)
        return await asyncio.gather(*tasks)

    async def async_miner_responses(self, addresses, miner_request):
        async with aiohttp.ClientSession() as http_client:
            responses = await self.fetch_all(http_client, miner_request, addresses)
            print(responses)
            return responses
        

if __name__ == "__main__":
    vali = Validator()
    asyncio.run(vali.voteloop())


