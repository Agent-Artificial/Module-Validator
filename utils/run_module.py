import os
import base64
from typing import Dict, Any
from module_validator.main import ModuleRegistry
from module_validator.config import Config
from module_validator.database import Database
from dotenv import load_dotenv
from loguru import logger
import subprocess
from module_validator.modules.translation.data_models import MinerRequest

load_dotenv()

ENV = os.getenv('MODULE_VALIDATOR_ENV', 'development')


def main(config_dir: str="module_validator/config", module_name: str="translation", input_data: Dict[str,Any]=None):
    environment = ["bash", "utils/set_environment.sh", module_name]
    subprocess.run(environment, check=True)
    config = Config(config_dir)

    config.load_configs()

    db = Database(config)


    registry = ModuleRegistry(config, db)

    registry.load_modules()

    module = registry.get_module(module_name)

    translation_request = MinerRequest(input_data)

    result = module(translation_request)
    result_string = base64.b64decode(result).decode("utf-8")
    logger.debug(result_string)

    
if __name__ == "__main__":
    data = {
        "input": "Hello, world!",
        "task_string": "text2text",
        "target_language": "French",
        "source_language": "English"
    }
    main(config_dir="module_validator/config", module_name="translation", input_data=data)