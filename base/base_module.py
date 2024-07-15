import os
import base64
import requests
import subprocess
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path

from data_models import ModuleConfig




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

    def get_public_key(self, key_name: str, public_key_path: Path):
        public_key = requests.get(f"{self.module_config.module_url}/modules/{key_name}", timeout=30).text
        if not os.path.exists("data"):
            os.makedirs("data")
        self.check_public_key()
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

    # TODO Rename this here and in `init_module` and `update_module`
    def install_module(self, module_config):
        self.get_module(module_config)
        self.setup_module(module_config)


if __name__ == "__main__":
    module_settings = ModuleConfig(
        module_name="translation",
        module_path="modules/translation",
        module_url="http://localhost:8000",
        module_endpoint="/modules/translation"
    )                
    module = BaseModule(module_settings)
    module.install_module(module_settings)