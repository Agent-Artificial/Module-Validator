import os
import io
import base64
from typing import Union, Optional
from fastapi import HTTPException
from dotenv import load_dotenv
from loguru import logger

from .data_models import TranslationRequest, MinerConfig, ModuleConfig, BaseMiner, TranslationConfig
from .translation import Translation

load_dotenv()


module_settings = ModuleConfig(
    module_path=os.getenv("MODULE_PATH"),
    module_name=os.getenv("MODULE_NAME"),
    module_endpoint=os.getenv("MODULE_ENDPOINT"),
    module_url="https://http://localhost:4267/"
)

miner_settings = MinerConfig(
    miner_name=os.getenv("MINER_NAME"),
    miner_keypath=os.getenv("KEYPATH_NAME"),
    miner_host=os.getenv("MINER_HOST"),
    external_address=os.getenv("EXTERNAL_ADDRESS"),
    miner_port=os.getenv("MINER_PORT"),
    stake=os.getenv("STAKE"),
    netuid=os.getenv("NETUID"),
    funding_key=os.getenv("FUNDING_KEY"),
    funding_modifier=os.getenv("MODIFIER"),
    module_name=os.getenv("MODULE_NAME")
)
translator = Translation(TranslationConfig())


class TranslationMiner(BaseMiner):
    
    def __init__(
        self,
        miner_config: MinerConfig,
        module_config: ModuleConfig
    ):
        """
        Initializes the TranslationMiner class with optional route, inpath, and outpath parameters.
        
        Parameters:
            miner_config (MinerConfig): The route for the translation.
            module_config (ModuleConfig): The input path for translation.
        """
        super().__init__(miner_config, module_settings)        
        os.makedirs(module_config.module_path, exist_ok=True)
        os.makedirs(f"{module_config.module_path}/in", exist_ok=True)
        os.makedirs(f"{module_config.module_path}/out", exist_ok=True)
    
    def process(self, miner_request: TranslationRequest) -> Union[str, bytes]:
        """
        Processes the given `TranslationRequest` object and returns the translation result.

        Parameters:
            miner_request (TranslationRequest): The request object containing the input data, task string, source language, and target language.

        Returns:
            Union[str, bytes]: The translation result.

        Raises:
            HTTPException: If an error occurs during the translation process.

        """
        try:
            return translator.process(miner_request)
        except Exception as e:
            logger.error(f"Error processing translation: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing translation: {e}") from e
    
        
miner = TranslationMiner(module_config=module_settings, miner_config=miner_settings)

miner.add_route(module_settings.module_name)

miner.run_server(miner_settings.miner_host, miner_settings.miner_port)
