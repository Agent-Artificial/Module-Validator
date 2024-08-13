# module_validator/config.py

import os
import yaml
from typing import Dict, Any

class Config:
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), 'config')
        self.environment = os.getenv('MODULE_VALIDATOR_ENV', 'development')
        self.global_config = {}
        self.module_configs = {}

    def load_configs(self):
        env_dir = os.path.join(self.config_dir, self.environment)
        
        if not os.path.exists(env_dir):
            raise ValueError(f"Configuration for environment '{self.environment}' not found.")

        # Load global config
        global_config_path = os.path.join(env_dir, 'global.yaml')
        if os.path.exists(global_config_path):
            with open(global_config_path, 'r') as f:
                self.global_config = yaml.safe_load(f)

        # Load module-specific configs
        for filename in os.listdir(env_dir):
            if filename.endswith('.yaml') and filename != 'global.yaml':
                module_name = filename[:-5]  # Remove '.yaml' from the end
                with open(os.path.join(env_dir, filename), 'r') as f:
                    self.module_configs[module_name] = yaml.safe_load(f)

    def get_global_config(self) -> Dict[str, Any]:
        return self.global_config

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        return self.module_configs.get(module_name, {})

    def get_config(self, module_name: str = None) -> Dict[str, Any]:
        if module_name:
            return {**self.global_config, **self.get_module_config(module_name)}
        return self.global_config

# Usage
config = Config()
config.load_configs()

# Get global config
global_config = config.get_global_config()

# Get config for a specific module (combines global and module-specific settings)
embedding_config = config.get_config('embedding')