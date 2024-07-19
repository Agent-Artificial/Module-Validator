import json
import subprocess
import uvicorn
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List, Union
from pydantic import BaseModel
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from base.base_module import BaseModule

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
