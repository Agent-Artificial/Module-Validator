# module_validator/config.py

import os
import yaml
from typing import Dict, Any

class Config:
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), 'config')
        self.global_config = {}
        self.module_configs = {}
        self.environment = os.getenv('MODULE_VALIDATOR_ENV', 'development')

    def load_configs(self):
        # Load global config
        global_config_path = os.path.join(self.config_dir, f'global_{self.environment}.yaml')
        if os.path.exists(global_config_path):
            with open(global_config_path, 'r') as f:
                self.global_config = yaml.safe_load(f)

        # Load module-specific configs
        for filename in os.listdir(self.config_dir):
            if filename.endswith(f'_{self.environment}.yaml') and not filename.startswith('global'):
                module_name = filename.split('_')[0]
                with open(os.path.join(self.config_dir, filename), 'r') as f:
                    self.module_configs[module_name] = yaml.safe_load(f)

    def get_global_config(self) -> Dict[str, Any]:
        return self.global_config

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        return self.module_configs.get(module_name, {})

    def get_config(self, module_name: str = None) -> Dict[str, Any]:
        if module_name:
            return {**self.global_config, **self.get_module_config(module_name)}
        return self.global_config

# Usage in main.py
from module_validator.config import Config

config = Config()
config.load_configs()

# In your ModuleRegistry class
class ModuleRegistry:
    def __init__(self, config: Config):
        self.config = config
        self.modules = {}

    def load_modules(self):
        # ... (previous implementation)
        
        # Pass configuration to modules
        for name, module in self.modules.items():
            if hasattr(module, 'configure'):
                module.configure(self.config.get_config(name))

# In your main function
def main():
    config = Config()
    config.load_configs()
    registry = ModuleRegistry(config)
    registry.load_modules()
    # ... (rest of your main function)