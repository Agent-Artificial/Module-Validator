import bittensor
import requests
import math
import json
from transformers import AutoTokenizer
from loguru import logger
from typing import Optional, Any
from bittensor.utils.weight_utils import process_weights_for_netuid
from chains.tao.neurons.miner import TAOMiner
from chains.tao.neurons.config import get_config
from data_models import ModuleConfig, MinerRequest
from chains.tao.axons.query_axions import ping_uids


config = get_config()

module_config = ModuleConfig(
    module_name="translation",
    module_path="modules/translation",
    module_endpoint="/modules/translation",
    module_url="https://registrar-cellium.ngrok.app"
)


class TAOValidator(TAOMiner):
    def __init__(self):
        super().__init__(module_config=module_config)
        self.wallet = bittensor.wallet(**config["wallet"])
        self.metagraph = bittensor.metagraph
        self.dendrite = bittensor.dendrite
        self.subtensor = bittensor.subtensor
        self.set_module(module_config)
        
    async def get_uids(self):
        return self.metagraph.hotkeys
        
    async def ping_uids(self, dendrite, metagraph, uids, timeout=30):
        return await ping_uids(dendrite, metagraph, uids, timeout=timeout)
    
    async def forward(self, sample_request: MinerRequest):
        return await self.module.process(miner_request=sample_request)
            
    async def get_sample_data(self, timeout=30):
        url = f"{self.module_config.module_url}{self.module_config.module_endpoint}/sample_request"
        try:
            response = requests.get(url, timeout=timeout)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request for sample data failed: {e}")
            return None
        return response.text
        
    def get_sample_request(self, request_data):
        return MinerRequest(dataa=request_data)
    
    async def get_sample_response(self, sample_request: MinerRequest):
        return await self.forward(sample_request)
    
    async def evaluate(self):
        sample_request = self.get_sample_request(await self.get_sample_data())
        sample_response = await self.get_sample_response(sample_request)
        uids = self.get_uids()
        responses = []
        try:
            for uid in uids:
                axon = self.metagraph.axons[uid]
                
                responses.append(requests.post(
                    axon.url,
                    data={
                        "input": sample_request.data["in_file"],
                        "task_string": sample_request.data["task_string"],
                        "source_langauge": sample_request.data["source_langauge"],
                        "target_languages": sample_request.data["target_languages"]
                },
                    timeout=30
                ))
        except Exception as e:
            logger.error(f"Error making requests for evaluation: {e}\n{sample_request.data}")
            return
        scores = {}
        sample_tokens = self.tokenize_response(sample_response)
        for response in responses:
            tokens = self.tokenize_response(response[0])
            scores[response[1]] = self.similarity(sample_tokens, tokens)
        uids, scores = list(self.sigmoid(scores).items())
        self.process_weights(uids, scores, 1, self.subtensor, self.metagraph)

    def tokenize_response(self, response):
        tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-de")
        return tokenizer.tokenize(response)
    
    def similarity(self, sample_tokens, tokens):
        return sum(sample_token in tokens for sample_token in sample_tokens) / len(
            sample_tokens
        )
                    
    def sigmoid(self, scores, threshold_multiplier=0.2):
        mean_score = sum(scores.values()) / len(list(scores.keys()))
        threshold = mean_score * (1 + threshold_multiplier)
        slope = 3.0
        max_value = 1.0
        min_value = 0.01
        
        final_scores = {}
        for uid, score in scores.items():
            normalized_score = (score - threshold) * slope
            sigmoid = 1 / (1 + math.exp(-normalized_score))
            final_scores[uid] = min_value + (max_value - min_value) * sigmoid
        return final_scores
    
    def process_weights(self, uids, weights, netuid, subtensor, metagraph, exclude_quantile=0):
        return process_weights_for_netuid(uids, weights, netuid, subtensor, metagraph, exclude_quantile)