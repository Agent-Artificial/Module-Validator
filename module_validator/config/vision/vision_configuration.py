from module_validator.config.base_configuration import GenericConfig, T
from typing import Union, Dict, Any, List
from pydantic import BaseModel, Field
import argparse
import os



class Config(GenericConfig):

    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump(
                exclude_unset = True
        )
        super().__init__(**data)
        
    def get(self, key: str, default: T = None) -> T:
        return self._get(key, default)
    
    def set(self, key: str, value: T) -> None:
        self._set(key, value)
        
    def merge(self, new_config: Dict[str, T]) -> Dict[str, Any]:
        self.config = self._merge(new_config, self.config)
        return self.config

    def load_config(self, parser: argparse.ArgumentParser, args: argparse.Namespace) -> 'Config':
        return self._load_config(parser, args)
    
    def parse_args(self, args: argparse.Namespace):
        self._parse_args(args)
    
    def add_args(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        return self._add_args(parser)
    
    def get_env(self) -> List[str]:
        lines = [

        ]
        return self._add_env(self.config)

    def add_args(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:

        parser.add_argument('--config', type=str, default=None, help='path to config file', required=False)
        return parser
