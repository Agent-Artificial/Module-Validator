from pydantic import BaseModel, Field
from typing import Any

class Axon(BaseModel):
    port: int = ''
    external_ip: str = ''

class Subtensor(BaseModel):
    network: str = ''
    chain_endpoint: str = ''

class Wallet(BaseModel):
    name: str = ''
    hotkey: str = ''

class Config(BaseModel):
    wallet: Any = None
    subtensor: Any = None
    neuron: Any = None
    axon: Any = None
    metagraph: Any = None
    axon: Axon = Field(default_factory=Axon)
    debug_miner: Any = None
    subtensor: Subtensor = Field(default_factory=Subtensor)
    netuid: Any = None
    wallet: Wallet = Field(default_factory=Wallet)

    def get(self, key: str, default: Any = None) -> Any:
        parts = key.split('.')
        value = self
        for part in parts:
            if isinstance(value, BaseModel):
                value = getattr(value, part, default)
            elif isinstance(value, dict):
                value = value.get(part, default)
            else:
                return default
            if value is None:
                return default
        return value

def prompt_for_values(config: Config):
    for field_name, field in config.__fields__.items():
        if isinstance(field.type_, type) and issubclass(field.type_, BaseModel):
            nested_config = getattr(config, field_name)
            print(f'Configuring {field_name}:')
            prompt_for_values(nested_config)
        else:
            default = getattr(config, field_name)
            description = field.field_info.description
            default_str = f' (default: {default})' if default is not None else ''
            prompt = f'Enter value for {field_name}{default_str}'
            if description:
                prompt += f' ({description})'
            prompt += ', or press Enter to keep default: '
            value = input(prompt)
            if value:
                try:
                    if field.type_ == bool:
                        typed_value = value.lower() in ('true', 'yes', '1', 'on')
                    elif field.type_ == int:
                        typed_value = int(value)
                    elif field.type_ == float:
                        typed_value = float(value)
                    else:
                        typed_value = value
                    setattr(config, field_name, typed_value)
                except ValueError:
                    print(f'Invalid input for {field_name}. Using default value.')
