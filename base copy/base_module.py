import os
import json
import base64
import requests
import subprocess
from pydantic import BaseModel
from pathlib import Path
from typing import Optional


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


if __name__ == "__main__":
    module_settings = ModuleConfig()
    module = BaseModule(module_settings)
