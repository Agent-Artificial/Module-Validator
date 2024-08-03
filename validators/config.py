from pydantic import BaseModel
import os
from dotenv import load_dotenv


load_dotenv()


class EnvironmentConfig(BaseModel):
    VALIDATOR_NAME: str
    VALIDATOR_KEYPATH: str
    VALIDATOR_HOST: str
    VALIDATOR_PORT: int
    FUNDING_KEY: str
    NETUID: int
    STAKE: int
    MODIFIER: int
    INFERENCE_URL: str
    INFERENCE_API_KEY: str
    INFERENCE_MODEL: str
    MODULE_NAME: str
    MODULE_PATH: str
    MODULE_ENDPOINT: str
    MODULE_URL: str


DEFAULT_CONFIG = EnvironmentConfig(
    VALIDATOR_NAME="eden.Validator",
    VALIDATOR_KEYPATH="eden.Validator",
    VALIDATOR_HOST="0.0.0.0",
    VALIDATOR_PORT="42069",
    FUNDING_KEY="eden.Valdiator",
    NETUID=10,
    STAKE=24000,
    MODIFIER=15,
    INFERENCE_URL="https://text-celium.ngrok.dev/v1",
    INFERENCE_API_KEY="sk-1234",
    INFERENCE_MODEL="meta-llama3-7b",
    MODULE_NAME="embedding",
    MODULE_PATH="modules/embdding",
    MODULE_ENDPOINT="/modules/embdding",
    MODULE_URL="https://registrar-cellium.ngrok.app"
)


def use_default_config():
    environ = os.environ
    for key, value in DEFAULT_CONFIG.model_dump().items():
        if key not in environ or value is None:
            environ[key] = str(value)