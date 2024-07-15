import os
import torch
import json
import requests
import base64
import subprocess
from pathlib import Path
from loguru import logger
from pydantic import BaseModel, Field
from typing import Dict, Union, Optional, Any
from abc import ABC, abstractmethod
from fastapi import APIRouter, FastAPI
from substrateinterface.keypair import Keypair
from communex._common import get_node_url
from communex.client import CommuneClient

comx = CommuneClient(get_node_url())

app = FastAPI()

TASK_STRINGS = {
    "speech2text": "s2tt",
    "speech2speech": "s2st",
    "auto_speech_recognition": "asr",
    "text2speech": "t2st",
    "text2text": "t2tt",
}

TARGET_LANGUAGES = {
    "English": "eng",
    "Afrikaans": "afr",
    "Amharic": "amh",
    "Modern Standard Arabic": "arb",
    "Moroccan Arabic": "ary",
    "Egyptian Arabic": "arz",
    "Assamese": "asm",
    "Asturian": "ast",
    "North Azerbaijani": "azj",
    "Belarusian": "bel",
    "Bengali": "ben",
    "Bosnian": "bos",
    "Bulgarian": "bul",
    "Catalan": "cat",
    "Cebuano": "ceb",
    "Czech": "ces",
    "Central": "ckb",
    "Mandarin Chinese": "cmn",
    "Mandarin Chinese Hant": "cmn_Hant",
    "Welsh": "cym",
    "Danish": "dan",
    "German": "deu",
    "Estonian": "est",
    "Basque": "eus",
    "Finnish": "fin",
    "French": "fra",
    "Nigerian Fulfulde": "fuv",
    "West Central Oromo": "gaz",
    "Irish": "gle",
    "Galician": "glg",
    "Gujarati": "guj",
    "Hebrew": "heb",
    "Hindi": "hin",
    "Croatian": "hrv",
    "Hungarian": "hun",
    "Armenian": "hye",
    "Igbo": "ibo",
    "Indonesian": "ind",
    "Icelandic": "isl",
    "Italian": "ita",
    "Javanese": "jav",
    "Japanese": "jpn",
    "Kamba": "kam",
    "Kannada": "kan",
    "Georgian": "kat",
    "Kazakh": "kaz",
    "Kabuverdianu": "kea",
    "Halh Mongolian": "khk",
    "Khmer": "khm",
    "Kyrgyz": "kir",
    "Korean": "kor",
    "Lao": "lao",
    "Lithuanian": "lit",
    "Luxembourgish": "ltz",
    "Ganda": "lug",
    "Luo": "luo",
    "Standard Latvian": "lvs",
    "Maithili": "mai",
    "Malayalam": "mal",
    "Marathi": "mar",
    "Macedonian": "mkd",
    "Maltese": "mlt",
    "Meitei": "mni",
    "Burmese": "mya",
    "Dutch": "nld",
    "Norwegian Nynorsk": "nno",
    "Norwegian Bokmål": "nob",
    "Nepali": "npi",
    "Nyanja": "nya",
    "Occitan": "oci",
    "Odia": "ory",
    "Punjabi": "pan",
    "Southern Pashto": "pbt",
    "Western Persian": "pes",
    "Polish": "pol",
    "Portuguese": "por",
    "Romanian": "ron",
    "Russian": "rus",
    "Slovak": "slk",
    "Slovenian": "slv",
    "Shona": "sna",
    "Sindhi": "snd",
    "Somali": "som",
    "Spanish": "spa",
    "Serbian": "srp",
    "Swedish": "swe",
    "Swahili": "swh",
    "Tamil": "tam",
    "Telugu": "tel",
    "Tajik": "tgk",
    "Tagalog": "tgl",
    "Thai": "tha",
    "Turkish": "tur",
    "Ukrainian": "ukr",
    "Urdu": "urd",
    "Northern Uzbek": "uzn",
    "Vietnamese": "vie",
    "Xhosa": "xho",
    "Yoruba": "yor",
    "Cantonese": "yue",
    "Colloquial Malay": "zlm",
    "Standard Malay": "zsm",
    "Zulu": "zul",
}


class MinerRequest(BaseModel):
    data: Any = Field(default=None)


class TranslationConfig(BaseModel):
    model_name_or_card: Union[str, Any] = "seamlessM4T_V2_large"
    vocoder_name: str = (
        "vocoder_v2"
        if model_name_or_card == "seamlessM4T_V2_large"
        else "vocoder_36langs"
    )
    device: Any = torch.device(device="cuda:0")
    text_tokenizer: str = model_name_or_card
    apply_mintox: bool = (True,)
    dtype: Any = (torch.float16,)
    input_modality: Optional[Any] = (None,)
    output_modality: Optional[Any] = None


class TranslationData(BaseModel):
    input: str
    task_string: str
    source_language: Optional[str] = None
    target_language: str


class TranslationRequest(MinerRequest):
    def __init__(self, data: TranslationData):
        super().__init__()
        self.data = data
        
        
class ModuleConfig(BaseModel):
    module_name: str = Field(default="module_name")
    module_path: str = Field(default="modules/{module_name}")
    module_endpoint: str = Field(default="/modules/{module_name}")
    module_url: str = Field(default="http://localhost")
    __pydantic_field_set__ = {"module_name", "module_path", "module_endpoint", "module_url"}
    
    
class MinerConfig(BaseModel):
    module_config: ModuleConfig = Field(default_factory=ModuleConfig)
    miner_key_dict: Dict[str, Any] = Field(default_factory=dict)
    key_name: str = Field(default="test_miner_1")


class BaseMiner(ABC):
    module_config: ModuleConfig = Field(default_factory=ModuleConfig)
    miner_key_dict: Dict[str, Any] = Field(default_factory=dict)
    key_name: str = Field(default="test_miner_1")
    
    def __init__(self, module_config: ModuleConfig, miner_config: MinerConfig):
        self.module_config = module_config
        self.miner_config = miner_config
        self.router = APIRouter()

    def add_route(self, module_name: str):
        @self.router.post(f"/modules/{module_name}/process")
        def process_request(request: MinerRequest):
            return self.process(request)
        app.include_router(self.router)

    @staticmethod
    def run_server(host_address: str, port: int):
        import uvicorn
        uvicorn.run(app, host=host_address, port=port)

    @staticmethod
    def get_miner_keys(keypath: Optional[str] = None):
        keypath = keypath or os.getenv("MINER_KEYPATH")
        return json.loads(Path(keypath).read_text(encoding="utf-8"))

    def add_miner_key(self, key_name: str, miner_keypath: Path = Path("data/miner_keys.json")):
        self.miner_key_dict[key_name] = MinerConfig().model_dump()
        self._save_miner_keys(miner_keypath)

    def remove_miner_key(self, key_name: str, miner_keypath: Path):
        self.miner_key_dict.pop(key_name, None)
        self._save_miner_keys(miner_keypath)

    def update_miner_key(self, key_name: str, miner_config: MinerConfig, miner_keypath: Path):
        self.miner_key_dict[key_name] = miner_config.model_dump()
        self._save_miner_keys(miner_keypath)

    def _save_miner_keys(self, miner_keypath: Path):
        miner_keypath.write_text(json.dumps(self.miner_key_dict), encoding="utf-8")

    def load_miner_keys(self, miner_keypath: Path):
        self.miner_key_dict = json.loads(miner_keypath.read_text(encoding="utf-8"))

    def get_keypair(self, key_name: str):
        key_folder_path = Path(self.module_config.key_folder_path)
        json_data = json.loads((key_folder_path / f"{key_name}.json").read_text(encoding='utf-8'))["data"]
        key_data = json.loads(json_data)
        return Keypair(key_data["private_key"], key_data["public_key"], key_data["ss58_address"])

    def register_miner(self, key_name: str, external_address: str, port: int, subnet: str, min_stake: int, metadata: str):
        address = f"{external_address}:{port}"
        keypair = self.get_keypair(key_name)
        result = comx.register_module(keypair, key_name, address, subnet, min_stake, metadata)
        return result.extrinsic

    def serve_miner(
        self,
        module_name: str, 
        key_name: str, 
        host_address: str, 
        external_address: str,
        port: int,
        subnet: str,
        min_stake: int,
        metadata: str,
        register: bool = False
    ):
        self.add_route(module_name)
        if register:
            self.register_miner(key_name, external_address, port, subnet, min_stake, metadata)
            logger.info(f"Registered {key_name} at {external_address}:{port}")
        self.run_server(host_address, port)

    @abstractmethod
    def process(self, miner_request: MinerRequest) -> Any:
        """Process a request made to the module."""
        

class BaseModule(BaseModel):
    module_config: ModuleConfig = Field(default_factory=ModuleConfig)
    __pydantic_fields_set__ = {"module_config"}
    
    def __init__(self, module_config: ModuleConfig):
        self.init_module(module_config)
        self.module_config = module_config
        
    def init_module(self, module_config: ModuleConfig):
        if os.path.exists(module_config.module_path):
            return
        if not os.path.exists(module_config.module_path):
            os.makedirs(module_config.module_path)
            self.install_module(module_config)
        
    def check_public_key(self):
        public_key_path = Path("data/public_key.pub")
        if Path(public_key_path).exists():
            pubkey = Path(public_key_path).read_text(encoding="utf-8")
            print(pubkey)
            pubkey_input = input("Public key exists. Do you want to overwrite it? (y/n) ")
            if pubkey_input.lower != "y" or pubkey_input != "" or pubkey_input.lower() != "yes":
                return pubkey
            else:
                public_key_path.unlink()

    def get_public_key(self, module_config: ModuleConfig, key_name: str = "public_key"):
        public_key = requests.get(f"{module_config.module_url}/modules/{key_name}", timeout=30).text
        if not os.path.exists("data"):
            os.makedirs("data")
        self.check_public_key()
        public_key_path = "data/public_key.pem"
        with open(public_key_path, "w", encoding="utf-8") as f:
            f.write(public_key)
        return public_key
        
    def check_for_existing_module(self, module_config: ModuleConfig):
        module_setup_path = Path(f"{module_config.module_path}/setup_{module_config.module_name}.py")
        if module_setup_path.exists():
            module = module_setup_path.read_text(encoding="utf-8")
            print(module)
            module_input = input("Module exists. Do you want to overwrite it? (y/n) ")
            if module_input.lower != "y" or module_input != "" or module_input.lower() != "yes":
                return module_setup_path.read_text(encoding="utf-8")
            else:
                self.remove_module(module_config)
                
    def get_module(self, module_config: ModuleConfig):
        module = requests.get(f"{module_config.module_url}{module_config.module_endpoint}", timeout=30).text
        module = self.from_base64(module)
        module_setup_path = Path(f"{module_config.module_path}/setup_{module_config.module_name}.py")
        self.check_for_existing_module(module_config)
        
        if not os.path.exists("modules"):
            os.makedirs("modules")
        if not os.path.exists(module_config.module_path):
            os.makedirs(module_config.module_path)

        with open(module_setup_path, "w", encoding="utf-8") as f:
            f.write(module)
        return module

    def from_base64(self, data):
        return base64.b64decode(data).decode("utf-8")
    
    def to_base64(self, data):
        return base64.b64encode(data.encode("utf-8"))
    
    def remove_module(self, module_config: ModuleConfig):
        os.removedirs(module_config.module_path)
        
    def save_module(self, module_config: ModuleConfig, module_data):
        with open(f"{module_config.module_path}/setup_{module_config.module_name}.py", "w", encoding="utf-8") as f:
            f.write(module_data)

    def setup_module(self, module_config: ModuleConfig):
        command = f"python {module_config.module_path}/setup_{module_config.module_name}.py"
        subprocess.run(command, shell=True, check=True)
        command = f"bash {module_config.module_path}/install_{module_config.module_name}.sh"
        subprocess.run(command, shell=True, check=True)

    def update_module(self, module_config: ModuleConfig):
        self.install_module(module_config)

    def install_module(self, module_config):
        self.get_module(module_config)
        self.setup_module(module_config)
     