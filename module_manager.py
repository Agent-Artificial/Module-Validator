import os
import json
import base64
import requests
import subprocess
from importlib import import_module
from typing import Dict, Any, Optional
from pydantic import BaseModel
from data_models import MinerConfig, ModuleConfig, BaseModule, app
from dotenv import load_dotenv

load_dotenv()

miner_config = MinerConfig(
    miner_name=os.getenv("MINER_NAME"),
    miner_keypath=os.getenv("KEYPATH_NAME"),
    miner_host=os.getenv("MINER_HOST"),
    external_address=os.getenv("EXTERNAL_ADDRESS"),
    miner_port=os.getenv("MINER_PORT"),
    stake=os.getenv("STAKE"),
    netuid=os.getenv("NETUID"),
    funding_key=os.getenv("FUNDING_KEY"),
    funding_modifier=os.getenv("MODIFIER"),
    module_name=os.getenv("MODULE_NAME"),
)


class ModuleManager:
    def __init__(self, module: BaseModule, module_config: ModuleConfig):
        """
        Initializes the ModuleManager with the given module.

        Parameters:
            module (BaseModule): The module to be initialized with.

        Returns:
            None
        """
        self.module_config = module_config
        self.module = module
        self.modules: Dict[str, Any] = {}
        self.active_modules: Dict[str, Any] = {}
        self.module_configs: Dict[str, Any] = self.get_configs()

    def get_configs(self) -> Dict[str, Any]:
        """
        Retrieves and returns the module configurations stored in the 'module_configs.json' file.

        Returns:
            Dict[str, Any]: A dictionary containing the module configurations.
        """
        config_path = "data/instance_data/module_configs.json"
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
            return {}

    def get_module(self):
        """
        Retrieves the modules based on the configurations stored in `module_configs`.
        It iterates through the module configurations, dynamically imports the module,
        and stores the module in the `modules` dictionary with the module name as the key.

        Returns:
            Dict: A dictionary containing the imported modules.
        """
        for config in self.module_configs.values():
            module_name = config["module_name"]
            for dir in os.listdir("modules"):
                if module_name in dir:
                    module = import_module(f"modules.{dir}.{module_name}")
                    self.modules[module_name] = module

        self.save_registry()
        return self.modules
    
    def add_module_config(
        self,
        module_conf: Optional[ModuleConfig] = None,
        module_name: Optional[str] = None,
        module_path: Optional[str] = None,
        module_endpoint: Optional[str] = None,
        module_url: Optional[str] = None,
    ):
        """
        Adds a module configuration to the `ModuleManager`.

        Args:
            module_name (Optional[str], optional): The name of the module. If not provided, the value from the environment variable `MODULE_NAME` or user input will be used. Defaults to None.
            module_path (Optional[str], optional): The path to the module. If not provided, the value from the environment variable `MODULE_PATH` or the default path `modules/{module_name}` will be used. Defaults to None.
            module_endpoint (Optional[str], optional): The endpoint of the module. If not provided, the value from the environment variable `MODULE_ENDPOINT` or the default endpoint `/modules/{module_name}` will be used. Defaults to None.
            module_url (Optional[str], optional): The URL of the module. If not provided, the value from the environment variable `MODULE_URL` or the default URL `http://localhost:4267` will be used. Defaults to None.

        Returns:
            module: The installed module.

        Raises:
            None.

        Notes:
            - This function checks if the module already exists.
            - It installs the module using the provided `module_config`.
            - It saves the `module_config` in `self.module_configs`.
            - It saves the module configurations.
            - It imports the module.
            - It saves the module in `self.modules`.
            - It sets the module as the current module.
            - It saves the module in the module registry.
            - It sets up the module.
        """
        if module_conf is None:
            if module_name is None:
                module_name = input("Enter module name: ")
                module_path = f"modules/{module_name}"
                module_endpoint = f"/modules/{module_name}"
                module_url = "https://registrar-cellium.ngrok.app"
            module_conf = ModuleConfig(
                module_name=module_name,
                module_path=module_path,
                module_endpoint=module_endpoint,
                module_url=module_url
            )
        module_config = module_conf
        self.module_configs[module_config.module_name] = module_config.model_dump()
        self.save_configs()
        return self.install_module(module_config)

    def install_module(self, module_config: ModuleConfig):
        """
        Installs a module based on the provided `ModuleConfig`.

        Args:
            module_config (ModuleConfig): The configuration for the module to install.

        Returns:
            module: The installed module.

        Raises:
            None.

        Notes:
            - This function checks if the module already exists.
            - It installs the module using the provided `module_config`.
            - It saves the `module_config` in `self.module_configs`.
            - It saves the module configurations.
            - It imports the module.
            - It saves the module in `self.modules`.
            - It sets the module as the current module.
            - It saves the module in the module registry.
            - It sets up the module.

        """
        self.module.check_for_existing_module()
        self.module.install_module(module_config)
        self.module_configs[module_config.module_name] = module_config.model_dump()
        self.save_configs()

        module = import_module(
            f"modules.{module_config.module_name}.{module_config.module_name}"
        )
        self.modules[module_config.module_name] = module
        self.module = module
        self.save_module(module_config, module)
        self.save_registry()
        return module

    def confirm_overwrite(self):
        """
        Confirms whether the user wants to overwrite an existing module.

        Returns:
            bool: True if the user wants to overwrite the module, False otherwise.
        """
        return input("Module already exists. Overwrite? [y/N]: ").lower() in [
            "y",
            "yes",
        ]

    def request_module(self, module_config: ModuleConfig):
        """
        A description of the request_module function which makes a request to a module URL
        and writes the response to a setup file.
        """
        try:
            response = requests.get(
                f"{module_config.module_url}/modules/{module_config.module_name}",
                timeout=30,
            )
            response.raise_for_status()
            setup_file = response.text
            with open(
                f"modules/{module_config.module_name}/setup_{module_config.module_name}.py",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(json.loads(setup_file))
        except requests.RequestException as e:
            print(f"Error requesting module: {e}")

    def setup_module(self, module_config: ModuleConfig):
        """
        Runs the setup process for the specified module configuration.

        Args:
            module_config (ModuleConfig): The configuration for the module.

        Raises:
            subprocess.CalledProcessError: If an error occurs during the setup process.
        """
        try:
            subprocess.run(
                [
                    "python",
                    "-m",
                    f"modules.{module_config.module_name}.setup_{module_config.module_name}",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error setting up module: {e}")

    def remove_module(self, module_config: ModuleConfig):
        """
        Removes a module from the active modules based on the provided module configuration.

        Args:
            module_config (ModuleConfig): The configuration of the module to be removed.

        Returns:
            Dict: The updated dictionary of active modules after removal.
        """
        self.active_modules.pop(module_config.module_name, None)
        return self.active_modules

    def save_module(self, module_config: ModuleConfig, module_data):
        """
        Saves the module data for a given module configuration.

        Args:
            module_config (ModuleConfig): The configuration for the module.
            module_data: The data to be saved.

        Returns:
            None
        """
        if module_config.module_name in self.active_modules:
            self.active_modules[module_config.module_name].save_module(
                module_config, module_data
            )

    def register_module(self, module_config: ModuleConfig):
        """
        Register a new module with the given module configuration.

        Parameters:
            self: the ModuleManager object
            module_config: an instance of ModuleConfig containing the module configuration

        Returns:
            None
        """
        self.module_configs[module_config.module_name] = module_config.model_dump()
        self.save_configs()
        self.save_registry()

    def save_configs(self):
        """
        Save the module configurations to a JSON file.

        No parameters are taken.

        No return value.
        """
        with open("data/instance_data/module_configs.json", "w", encoding="utf-8") as f:
            json.dump(self.module_configs, f, indent=4)

    def save_registry(self):
        """
        Saves the registry of modules to a JSON file.
        """
        with open("modules/registry.json", "w", encoding="utf-8") as f:
            json.dump(
                {name: str(module) for name, module in self.modules.items()},
                f,
                indent=4,
            )

    def list_modules(self):
        """
        Prints the list of active modules.

        This function iterates over the `self.modules` dictionary and prints each module name preceded by a hyphen.

        Parameters:
            None

        Returns:
            None
        """
        print("")
        print("Active Modules:")
        for name in self.modules:
            print(f"- {name}")

    def select_module(self):
        """
        Display a list of available modules and their corresponding indices.

        This function prints a list of available modules along with their indices.
        The modules are displayed in the format "{index}: {module_name}.".

        Parameters:
            self (object): The instance of the class.

        Returns:
            None
        """
        print("Available Modules:")
        for i, available_module in enumerate(self.modules.keys(), start=1):
            print(f"{i}: {available_module}.")
    
    def serve_module(self, module_config):
        module = import_module(f"modules.{module_config.module_name}.{module_config.module_name}_module")
        miner = module.TranslationMiner(miner_config=module.miner_settings, module_config=module.module_settings)
        miner.serve_miner(miner_config, reload=True, register=False)

    def cli(self):
        """
        A CLI function that displays options to the user, takes user input,
        and performs the corresponding action based on the input.
        """
        options = {
            "1": ("Add a Module Config", self.add_module_config),
            "2": ("Install Module", self.install_module_cli),
            "3": ("Select Module", self.get_module),
            "4": ("List Modules", self.list_modules),
            "5": ("Remove Module", self.remove_module),
            "6": ("Serve Module", self.serve_module),
            "7": ("Exit", exit),
        }

        while True:
            print("\nModule Manager CLI")
            for key, (description, _) in options.items():
                print(f"{key}. {description}")

            choice = input("Enter your choice: ")
            action = options.get(choice, (None, None))[1]
            if action:
                action(self.module_config)
            else:
                print("Invalid choice. Please try again.")

    def install_module_cli(self, module_config: ModuleConfig):
        """
        Installs a module based on user input.

        This function prompts the user to enter the name of a module. It then checks if the module name is present in the `module_configs` dictionary. If the module name is not found, it adds a new config for the module using the `add_module_config` method. If the module name is found, it creates a `ModuleConfig` object using the module name and the corresponding config from `module_configs`. Finally, it calls the `install_module` method with the `module_config` object to install the module.

        Parameters:
            None

        Returns:
            None
        """
        module_name = input("Enter module name: ")
        if module_name not in self.module_configs:
            print(f"Module '{module_name}' not found in configs. Adding new config.")
            self.add_module_config()
        else:
            module_config = ModuleConfig(**self.module_configs[module_name])
            self.install_module(module_config)


if __name__ == "__main__":
    module_config = ModuleConfig(
        module_name=os.getenv("MODULE_NAME"),
        module_path=os.getenv("MODULE_PATH"),
        module_endpoint=os.getenv("MODULE_ENDPOINT"),
        module_url=os.getenv("MODULE_URL"),
    )
    module = BaseModule(module_config)
    manager = ModuleManager(module, module_config)
    manager.cli()
