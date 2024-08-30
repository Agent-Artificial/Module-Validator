from pydantic import BaseModel, Field
from typing import Any
from dotenv import load_dotenv
import os

load_dotenv()




class Config(GenericConfig):
    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)



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
