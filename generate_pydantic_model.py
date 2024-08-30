from pydantic import BaseModel, Field
from typing import Type, Dict, Any

CONFIG_CLASS_TEMPLATE = """from module_validator.config.base_configuration import GenericConfig, T
from typing import Union, Dict, Any, List
from pydantic import BaseModel, Field
import argparse
import os

"{class_generation}"

class Config(GenericConfig):
"{attribute_generation}"
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
"{environment_generation}"
        ]
        return self._add_env(self.config)

    def add_args(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
"{argument_generation}"
        parser.add_argument('--config', type=str, default=None, help='path to config file', required=False)
        return parser

"""

FIELDS = ["name", "type", "help", "default", "action"]


def generate_pydantic_model(model_name: str, config: Dict[str, Any]) -> Type[BaseModel]:
    # Base class for all models
    class ConfigBaseModel(BaseModel):
        name: str
        type: str
        help: str

    # Creating dynamic model
    model_fields = {}
    print(config)
    # Iterate through the configuration to build the model fields
    for key, value in config.items():
        if '.' in key:
            # Nested key
            outer_key, inner_key = key.split('.', 1)
            if outer_key not in model_fields:
                nested_model = generate_pydantic_model(outer_key.capitalize() + 'Config', {inner_key: value})
                model_fields[outer_key] = (nested_model, None)
            elif inner_key not in model_fields and isinstance(value, dict) and any(field in value for field in fields):
                model_fields[outer_key][inner_key] = value
                model_fields[outer_key] = (nested_model, None)
                
                nested_model = model_fields[outer_key][0]
                nested_model.__annotations__[inner_key] = str
                if hasattr(value, "help"):
                    nested_model.__fields__[inner_key] = Field(default=None, description=value["help"])
        else:
            # Regular key
            model_fields = get_field_value(key, value, model_fields)

    # Create the new model dynamically
    return type(model_name, (ConfigBaseModel,), {'__annotations__': {k: v[0] for k, v in model_fields.items()}})



# Constants for template strings
ARGUMENT_LINE_TEMPLATE = "    parser.add_argument(\"--{name}\", default=\"{default}\", type={type}, help=\"{help}\", action=\"{action}\")\n"
ATTRIBUTE_LINE_TEMPLATE = "        {name}: {type} = Field(default=\"{default}\", description=\"{help}\", action=\"{action}\")\n"
ENVIRONMENT_LINE_TEMPLATE = "{name}={default}\n"
CLASS_LINE_TEMPLATE = "{name}: {type} = Field(description='{help}')\n"
CLASS_TEMPLATE = """
class {model_name}(BaseModel):
{attribute_generation}
"""

def get_field_value(name: str, value: dict, model_fields: dict) -> dict:
    model_fields["name"] = name
    model_fields["default"] = value.get("default", "")
    model_fields["type"] = value.get("type", "str")
    model_fields["help"] = value.get("help", "")
    model_fields["action"] = value.get("action", "")
    return model_fields
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field

FIELDS = ["name", "default", "type", "help", "action"]


def generate_pydantic_model_code(model_name: str, config: Dict[str, Any]) -> str:
    class_attribute_lines = []
    argument_lines = []
    attribute_lines = []
    environment_lines = []
    class_lines = []
    
    class_definitions = {}
    print(config)
    # Add fields to the model
    for key, value in config.items():
        model_fields = {}

        # Handle non-nested items
        if not isinstance(value, dict):
            model_fields["name"] = key
            model_fields["default"] = value
            model_fields["type"] = "str"
            model_fields["help"] = ""
            model_fields["action"] = ""

        # Handle nested structures
        elif isinstance(value, dict):
            if "." in key:
                name = key.split(".")[0].title()
                classname = name + "Config"
                attribute = key.split(".")[1]
                
                if classname not in class_definitions:
                    class_definitions[classname] = {
                        "template": "class {classname}(BaseModel):\n",
                        "config_dict": value,
                        "lines": []
                    }
                
                model_fields = get_field_value(attribute, value, model_fields)
                subclass_lines.append(ATTRIBUTE_LINE_TEMPLATE.format(**model_fields))
            else:
                model_fields = get_field_value(key, value, model_fields)

        else:
            # Skip list handling (adjust this based on your specific needs)
            print(f"Skipping list: {key}")
            continue
        
        # Append lines for the main class
        attribute_lines.append(ATTRIBUTE_LINE_TEMPLATE.format(**model_fields))
        argument_lines.append(ARGUMENT_LINE_TEMPLATE.format(**model_fields))
        environment_lines.append(ENVIRONMENT_LINE_TEMPLATE.format(**model_fields))
    print(attribute_lines)
    # Handle subclass templates
    subclass_lines = []
    for classname, class_def in class_definitions.items():
        subclass_template = class_def["template"].format(classname=classname)
        subclass_lines.append(subclass_template)
        subclass_lines.extend(class_def["lines"])

    # Combine everything into the final class code
    class_code = CLASS_TEMPLATE.format(
        model_name=model_name,
        attribute_generation="".join(subclass_lines)
    )
    print(attribute_lines, argument_lines, environment_lines, class_lines)
    return class_code, argument_lines, argument_lines, environment_lines, class_lines

def generate_script(config_dict: Dict[str, Dict[str, Any]], output_file: str) -> None:
    class_code, attribute_template, argument_template, environment_template, class_template = generate_pydantic_model_code("GenericConfig", config_dict)
    with open(output_file, "w") as file:
        file.write(class_code)        
    
    print(f"Script generated and saved to {output_file}")
    
    return class_code, attribute_template, argument_template, environment_template, class_template


if __name__ == "__main__":
    config_dict = {
        "--netuid": {"name": "--netuid", "type": "int", "help": "Network Unique ID"},
        "--neuron.disable_set_weights": {
            "name": "--neuron.disable_set_weights",
            "type": "bool",
            "help": "Disable setting weights",
        },
    }
    generate_script(config_dict, "module_validator/config/sylliba")

