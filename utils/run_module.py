import asyncio
import os
import base64
import json
from typing import Dict, Any
from module_validator.main import ModuleRegistry
from module_validator.config import Config
from module_validator.database import Database
from dotenv import load_dotenv
from loguru import logger
import subprocess
from module_validator.modules.translation.data_models import TranslationRequest

load_dotenv()

ENV = os.getenv('MODULE_VALIDATOR_ENV', 'development')


async def main(config_dir: str="module_validator/config", module_name: str="translation", input_data: Dict[str,Any]=None):
    logger.info("Configuring module...")
    environment = ["bash", "utils/set_environment.sh", module_name]
    subprocess.run(environment, check=True)
    config = Config(config_dir)

    config.load_configs()

    db = Database(config)
    
    registry = ModuleRegistry(config, db)

    registry.load_modules()

    module = registry.get_module(module_name)
    
    logger.debug(f"Module loaded {module}")

    translation_request = TranslationRequest(input_data)

    result = await module(translation_request.model_dump())
    return base64.b85decode(result.decode("utf-8")) if isinstance(result, bytes) else result
    

    
if __name__ == "__main__":
    from module_validator.modules.translation.data_models import TARGET_LANGUAGES, TASK_STRINGS
    data_map = {
        "1": "translation",
        "2": "embedding",
        "3": "financialnews"
    }
    task_map = {
        "1": "text2text",
        "2": "text2speech",
        "3": "speech2text",
        "4": "speech2speech"
    }
    def get_taskstring():
        for value, name in task_map.items():
            print(f"{value}. {name}")
        return input("Select task string: ")
        
    def get_target_language():
        for language, name in TARGET_LANGUAGES.items():
            print(f"{language}. {name}")
        return input("Select target language: ")
        
    def get_source_language():
        for language, name in TARGET_LANGUAGES.items():
            print(f"{language}. {name}")
        return input("Select source language: ")
        

    input_data=None
    params={}
    for key, value in data_map.items():
        print(f"{key}. {value}")
    choice = input("Select module to run(1-3): ")
    if choice == "1":
        input_data = input("Enter text to translate: ")
        task_string = task_map[str(choice)]
        target_language = get_target_language()
        for key, value in TARGET_LANGUAGES.items():
            if target_language == value:
                target_language = key
        source_language = get_source_language()
        for key, value in TARGET_LANGUAGES.items():
            if source_language == value:
                source_language = key
        data={
                "input": input_data,
                "task_string": task_string,
                "target_language": target_language,
                "source_language": source_language
            }
    if choice =="2":
        data = input("Enter text to embed: ")
    if choice == "3":
        data = input("Enter coma delineated list of tickers to search: ").split(",")
    
    logger.debug(data)
    result = asyncio.run(main(config_dir="module_validator/config", module_name=data_map[choice], input_data=data))
    logger.debug(result)