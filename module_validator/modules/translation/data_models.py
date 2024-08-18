import os
import base64
import requests
import torch
import json
import subprocess
import uvicorn
from pydantic import BaseModel, ConfigDict
from typing import Union, Optional, Any, Dict, List
from substrateinterface.utils import ss58
from pathlib import Path
from abc import ABC, abstractmethod
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware


class ModuleConfig(BaseModel):
    module_name: Optional[str] = None
    module_path: Optional[str] = None
    module_endpoint: Optional[str] = None
    module_url: Optional[str] = None


class BaseModule(BaseModel):
    module_config: Optional[ModuleConfig] = None

    def __init__(self, module_config: ModuleConfig):
        """
        Initializes a new instance of the BaseModule class.

        Args:
            module_config (ModuleConfig): The configuration for the module.

        Returns:
            None

        This method initializes an instance of the BaseModule class with the provided module configuration. It sets the `module_config` attribute to the provided `module_config` and calls the `init_module` method.
        """
        super().__init__(module_config=module_config)
        self.module_config = module_config
        self.init_module()

    def init_module(self):
        """
        Initializes the module by creating the necessary directories if they do not exist and installs the module based on the provided configuration.
        """
        if not os.path.exists(self.module_config.module_path):
            os.makedirs(self.module_config.module_path)
            self.install_module(self.module_config)

    def _check_and_prompt(self, path: Path, message: str) -> Optional[str]:
        """
        Check if a file exists at the given path and prompt the user to overwrite it if it does.

        Args:
            path (Path): The path to the file.
            message (str): The message to display to the user before prompting.

        Returns:
            Optional[str]: If the file exists and the user chooses to overwrite it, returns None.
                           If the file does not exist, returns None.
                           If the file exists and the user chooses not to overwrite it, returns the content of the file.
        """
        if path.exists():
            content = path.read_text(encoding="utf-8")
            print(content)
            user_input = input(f"{message} Do you want to overwrite it? (y/n) ").lower()
            return None if user_input in ["y", "yes"] else content
        return None

    def check_public_key(self) -> Optional[str]:
        """
        Check if a public key exists at the specified path and prompt the user based on the existence of the key.

        Returns:
            Optional[str]: If the public key exists and the user chooses not to overwrite it, returns the content of the key.
                           If the public key does not exist or the user chooses to overwrite it, returns None.
        """
        public_key_path = Path("data/public_key.pub")
        return self._check_and_prompt(public_key_path, "Public key exists.")

    def get_public_key(
        self, key_name: str = "public_key", public_key_path: str = "data/public_key.pem"
    ):
        """
        Retrieves the public key for a specified key name from a given module URL.

        Args:
            self: The object instance.
            key_name (str): The name of the key to retrieve. Defaults to "public_key".
            public_key_path (str): The path to save the public key. Defaults to "data/public_key.pem".

        Returns:
            str: The public key retrieved or the existing key if it exists.
        """
        public_key = requests.get(
            f"{self.module_config.module_url}/modules/{key_name}", timeout=30
        ).text
        os.makedirs("data", exist_ok=True)
        existing_key = self.check_public_key()
        if existing_key is None:
            Path(public_key_path).write_text(public_key, encoding="utf-8")
        return existing_key or public_key

    def check_for_existing_module(self) -> Optional[str]:
        """
        Check for an existing module setup file at the specified path and return the result.
        """
        module_setup_path = Path(
            f"{self.module_config.module_path}/setup_{self.module_config.module_name}.py"
        )
        return self._check_and_prompt(module_setup_path, "Module exists.")

    def get_module(self):
        """
        A description of the entire function, its parameters, and its return types.
        """
        name = os.getenv("MODULE_NAME")
        endpoint = os.getenv("MODULE_ENDPOINT")
        url = os.getenv("MODULE_URL")
        filepath = f"{os.getenv('MODULE_PATH')}/setup_{name}.py"
        
        module = json.loads(requests.get(f"{url}{endpoint}").json())
        
        filepath = Path(filepath)
        
        if not filepath.exists():
            filepath.parent.mkdir(parents=True)
        
        filepath.write_text(json.loads(module))
        
        return module

    def remove_module(self):
        """
        Removes the module directory specified in the module configuration.

        This function uses the `Path` class from the `pathlib` module to remove the module directory specified in the `module_path` attribute of the `module_config` object. The `rmdir()` method is called on the `Path` object to remove the directory.

        Parameters:
            self (BaseModule): The instance of the `BaseModule` class.

        Returns:
            None
        """
        Path(self.module_config.module_path).rmdir()

    def save_module(self, module_data: str):
        """
        Saves the module data to a file at the specified path.

        Args:
            self (BaseModule): The instance of the BaseModule class.
            module_data (str): The module data to be saved.

        Returns:
            None
        """
        Path(
            f"{self.module_config.module_path}/setup_{self.module_config.module_name}.py"
        ).write_text(base64.b16decode(module_data).decode("utf-8"), encoding="utf-8")

    def setup_module(self):
        """
        Executes the setup module command using the `subprocess.run` function.

        This function takes no parameters.

        It uses the `subprocess.run` function to execute the setup module command. The command is constructed using the `module_config.module_path` and `module_config.module_name` attributes. The `module_path` is replaced with dots ('.') to match the Python module naming convention. The command is passed to `subprocess.run` with the `check=True` parameter to raise an exception if the command fails.

        This function does not return anything.
        """
        subprocess.run(
            [
                "python",
                "-m",
                f"{self.module_config.module_path.replace('/', '.')}.setup_{self.module_config.module_name}",
            ],
            check=True,
        )

    def update_module(self, module_config: ModuleConfig):
        """
        Updates the module by installing it using the provided module configuration.

        Args:
            module_config (ModuleConfig): The configuration for the module to update.

        Returns:
            None
        """
        self.install_module(module_config=module_config)

    def install_module(self, module_config: ModuleConfig):
        self.module_config = module_config
        self.get_module()
        self.setup_module()
        subprocess.run(
            [
                "bash",
                f"{self.module_config.module_path}/install_{self.module_config.module_name}.sh",
            ],
            check=True,
        )
        
        
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MinerRequest(BaseModel):
    data: Optional[Any] = None


class MinerConfig(BaseModel):
    miner_name: Optional[str] = None
    miner_keypath: Optional[str] = None
    miner_host: Optional[str] = None
    external_address: Optional[str] = None
    miner_port: Optional[int] = None
    stake: Optional[float] = None
    netuid: Optional[int] = None
    funding_key: Optional[str] = None
    funding_modifier: Optional[float] = None
    module_name: Optional[str] = None


class BaseMiner(ABC):
    miner_config: Optional[Union[MinerConfig, Dict[str, Any]]] = {}
    miner_configs: Optional[Dict[str, Union[MinerConfig, Dict[str, Any]]]] = {}
    miners: Optional[Dict[str, Any]] = {}
    router: Optional[APIRouter] = None
    module: Optional[BaseModule] = None

    def __init__(self, miner_config: MinerConfig, module: BaseModule):
        """
        Initializes a new instance of the BaseMiner class.

        Args:
            miner_config (MinerConfig): The configuration for the miner.
            module (BaseModule): The module to be used by the miner.

        Returns:
            None
        """
        self.miner_config = miner_config
        self.miner_configs = self._load_configs("modules/miner_configs.json")
        self.router = APIRouter()
        self.module = module

    def _load_configs(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load configurations from a JSON file.

        Args:
            file_path (str): The path to the JSON file containing the configurations.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the configurations.
                If the file does not exist, an empty list is returned.

        Raises:
            None
        """
        path = Path(file_path)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        configs = []
        path.write_text(json.dumps(configs, indent=4), encoding="utf-8")
        return configs

    def add_route(self, module: BaseModule):
        """
        Adds a route to the FastAPI app for the specified module.
        The route handles GET requests to '/modules/{request.module_name}/process'
        and processes the request by instantiating the module with the provided configuration
        and calling its 'process' method.

        Parameters:
        - module: BaseModule - The module to be used for processing the request.
        - app: FastAPI - The FastAPI application to add the route to.

        Returns:
        - None
        """
        router = APIRouter()
        request_module = module

        @router.get("/modules/{request.module_name}/process")
        async def process_request(request: MinerRequest):
            """
            Process a request for a specific module.

            This function is a route handler for GET requests to '/modules/{request.module_name}/process'.
            It receives a `MinerRequest` object as a parameter, which contains information about the module to be processed.
            The function creates a `module_config` dictionary with the necessary information from the request.
            It then uses the `request_module` function to instantiate a module with the provided configuration.
            Finally, it calls the `process` method of the module with the request as an argument and returns the result.

            Parameters:
            - request (MinerRequest): The request object containing information about the module to be processed.

            Returns:
            - The result of calling the `process` method of the module with the request as an argument.
            """
            module_config = {
                "module_name": request.module_name,
                "module_path": request.module_path,
                "module_endpoint": request.module_endpoint,
                "module_url": request.module_url,
            }
            module = request_module(**module_config)
            return await module.process(request)

        app.include_router(router)

    def _prompt_miner_config(self) -> MinerConfig:
        """
        Prompts the user to enter miner configuration details and returns a MinerConfig object.

        Parameters:
        - None

        Returns:
        - MinerConfig: An object containing the miner configuration details entered by the user.
        """
        return MinerConfig(
            miner_name=input("Enter miner_name: "),
            miner_keypath=input(
                "Enter miner_keypath [ex. $HOME/.commune/key/my_miner.json]: "
            )
            or None,
            miner_host=input("Enter miner_host [default 0.0.0.0]: ") or "0.0.0.0",
            external_address=input("Enter external_address: ") or None,
            miner_port=int(input("Enter miner_port [default 5757]: ") or 5757),
            stake=float(input("Enter stake [default 275COM]: ") or 275),
            netuid=int(input("Enter netuid [default 0]: ") or 0),
            funding_key=input("Enter funding_key: "),
            funding_modifier=float(input("Enter modifier [default 15COM]: ") or 15),
        )

    def serve_miner(
        self,
        miner_config: MinerConfig,
        reload: Optional[bool] = True,
        register: bool = False,
    ):
        """
        Serves the miner with the specified miner configuration.

        Parameters:
        - self: The BaseMiner object.
        - miner_config: MinerConfig - The configuration for the miner.
        - reload: Optional[bool] - Whether to reload the miner. Defaults to True.
        - register: bool - Whether to register the miner or not.

        Returns:
        - None
        """
        if register:
            self.register_miner(miner_config)
        uvicorn.run(
            "api:app",
            host=miner_config.miner_host,
            port=miner_config.miner_port,
            reload=reload,
        )

    def register_miner(self, miner_config: MinerConfig):
        """
        Registers a new miner using the provided miner configuration.

        Parameters:
        - self: The BaseMiner object.
        - miner_config: MinerConfig - The configuration for the miner.

        Returns:
        - None
        """
        command = [
            "bash",
            "chains/commune/register_miner.sh",
            "register",
            f"{miner_config.miner_name}",
            f"{miner_config.miner_keypath}",
            f"{miner_config.miner_host}",
            f"{miner_config.port}",
            f"{miner_config.netuid}",
            f"{miner_config.stake}",
            f"{miner_config.funding_key}",
            f"{miner_config.modifier}",
        ]
        subprocess.run(command, check=True)

    @abstractmethod
    def process(self, miner_request: MinerRequest) -> Any:
        """
        Process the given `MinerRequest` using the `module` and return the result.

        Args:
            miner_request (MinerRequest): The request to be processed.

        Returns:
            Any: The result of the processing.
        """
        self.module.process(miner_request)


class Ss58Key:
    ss58_address: str
    folder_path: str

    def __init__(self, address: str, folder_path: str = "$HOME/.commune/key") -> None:
        super().__init__()
        self.ss58_address = self.add_address(address)
        self.folder_path = folder_path

    def add_address(self, key_info: str) -> str:
        if key_info.startswith("0x"):
            encoded_address = ss58.ss58_encode(key_info)
        if key_info.startswith("5"):
            encoded_address = key_info
        else:
            try:
                encoded_address = self.get_keyfile_path(key_info)["ss58_address"]
            except FileNotFoundError:
                encoded_address = ss58.ss58_encode(key_info)
        self.__setattr__("ss58_address", encoded_address)
        return encoded_address

    def encode(self, public_address: str) -> str:
        return ss58.ss58_encode(public_address)

    def get_keyfile_path(self, key_name: str) -> str:
        with open(f"{self.folder_path}/{key_name}.json", "r", encoding="utf-8") as f:
            json_data = json.loads(f.read())["data"]
            return json.loads(json_data)

    def __str__(self) -> str:
        return str(self.ss58_address)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "ss58_address":
            return super().__setattr__(name, value)
        return super().__setattr__(name, self.encode(value))

    def __hash__(self) -> int:
        return hash(self.ss58_address)

    def __get_pydantic_core_schema__(self, _config: ConfigDict) -> Dict[str, Any]:
        return {"ss58_address": str}


class RegistrarConfig:
    module_name: str
    storage_path: str
    target_modules_path: str


__all__ = [
    "Ss58Key",
    "MinerRequest",
    "MinerConfig",
    "ModuleConfig",
    "BaseModule",
    "BaseMiner",
    "app",
    "RegistrarConfig",
]


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


class TranslationConfig(BaseModel):
    model_name_or_card: Union[str, Any] = "facebook/seamless-M4T-V2-large"
    vocoder_name: str = (
        "vocoder_v2"
        if model_name_or_card == "facebook/seamless-M4T-V2-large"
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

   
__all__ = [
    "TranslationConfig",
    "TranslationData",
    "TranslationRequest",
    "TARGET_LANGUAGES",
    "TASK_STRINGS",
    "MinerConfig",
    "ModuleConfig",
    "BaseMiner",
    "BaseModule",
    "app",
    "Ss58Key"
]