import json
import argparse
from pydantic import BaseModel
from typing import Dict, Any, Union, TypeVar, List

T = TypeVar("T")


class GenericConfig(BaseModel):
    config: Dict[str, T] = {}

    @classmethod
    def __init__(cls, data: Union[BaseModel, Dict[str, Any]]):
        config_data = data.model_dump() if isinstance(data, BaseModel) else data
        super().__init__(**config_data)
        cls.config = cls._merge(config_data, cls.config) if cls.config else config_data

    @classmethod
    def _get(cls, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = cls.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    @classmethod
    def _set(cls, key: str, value: Any):
        keys = key.split(".")
        d = cls.config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    @classmethod
    def _merge(
        cls, new_config: Dict[str, Any], old_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        merged_config = old_config.copy()
        for key, value in new_config.items():
            if (
                isinstance(value, dict)
                and key in merged_config
                and isinstance(merged_config[key], dict)
            ):
                merged_config[key] = cls._merge(value, merged_config[key])
            else:
                merged_config[key] = value
        return merged_config

    @classmethod
    def _load_config(
        cls, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> "GenericConfig":
        config = cls(config={})
        config._parse_args(args)
        return config

    @classmethod
    def _parse_args(cls, args: argparse.Namespace):
        for arg, value in vars(args).items():
            if value is not None:
                cls._set(arg, value)


if __name__ == "__main__":

    config = GenericConfig(config={})
