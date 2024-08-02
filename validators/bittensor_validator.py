import os
import time
import uvicorn
import asyncio
from loguru import logger
from fastapi import FastAPI
from typing import List, Any, Dict
from dotenv import load_dotenv
from data_models import ModuleConfig
from base.base_validator import ValdiatorExecutor, ValidatorSettings

load_dotenv()

settings = ValidatorSettings()

module_config = ModuleConfig(
    module_name=os.getenv("MODULE_NAME"),
    module_path=os.getenv("MODULE_PATH"),
    module_endpoint=os.getenv("MODULE_ENDPOINT"),
    module_url=os.getenv("MODULE_URL")
)

class CommuneValidator():
    def __init__(self):
        super().__init__()
        self.module_config = module_config
        
    def serve_api(self, app: FastAPI):
        uvicorn.run(app, host="0.0.0.0", port=4268)
    
    async def voteloop(self):
        while True:
            await self.evaluate()
            time.sleep(30)
            
            
if __name__ == "__main__":
    vali = BittensorValidator()
    asyncio.run(vali.voteloop())