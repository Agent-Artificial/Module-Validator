import os
import re
import ast
import yaml
from typing import Dict, Any, List, ClassVar, Union, Tuple
from pathlib import Path
from pydantic import Field, create_model
from loguru import logger


CONFIG_CLASS_TEMPLATE = """from pydantic import BaseModel, Field
from typing import Any, Union, Dict, List, Optional, ClassVar
from pydantic import ConfigDict
from dotenv import load_dotenv
from module_validator.config.base_configuration import GenericConfig, T
import bittensor as bt
import argparse
import os

load_dotenv()

<<sub_class_generation>>

class Config(GenericConfig):
    model_config: ClassVar[ConfigDict] = ConfigDict({
            "aribtrary_types_allowed": True
    })
    config: Optional[bt.config] = Field(default_factory=bt.config, type=None)
    axon: Optional[bt.axon] = Field(default_factory=bt.axon, type=None)
    wallet: Optional[bt.wallet] = Field(default_factory=bt.wallet, type=None)
    metagraph: Optional[T] = Field(default_factory=bt.metagraph, type=None)
    subtensor: Optional[bt.subtensor] = Field(default_factory=bt.subtensor, type=None)
    dendrite: Optional[bt.dendrite] = Field(default_factory=bt.dendrite, type=None)
    hotkeypair: Optional[bt.Keypair] = Field(default_factory=bt.Keypair, type=None)
<<attribute_generation>>
    
    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        model_config: ConfigDict = ConfigDict({
            "aribtrary_types_allowed": True
        })

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
<<environment_generation>>
        ]
        return self._add_env(self.config)

    def add_args(self, parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        parser.add_argument('--config', type=str, default=None, help='path to config file', required=False)
<<argument_generation>>
        return parser


"""
SUB_CLASS_TEMPLATE = """
class {sub_classname}(GenericConfig):
<<sub_class_attribute_generation>>
    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        
"""
ATTRIBUTE_TEMPLATE = """    {name}: {type} = Field({model_fields})\n"""
SUBCLASS_ATTRIBUTE_TEMPLATE = "    {sub_classname}: {full_classname} = Field(default_factory={full_classname}, {model_fields})\n"
COMMAND_LINE_ARG_TEMPLATE = '        parser.add_argument("--{name}", default="{default}", type={type}, help="{help}", action="{action}")\n'
SUB_CLASS_LINES = []
CLASS_LINES = []
ENVIRONMENT_LINES = []
ARGUMENT_LINES = []
ATTRIBUTE_LINES = []


def extract_argparse_arguments(file_path: str) -> List[Dict[str, Any]]:
    logger.info(f"\nExtracting arguments from {file_path}")
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    arguments = []

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument"
        ):
            try:
                arg_info = parse_add_argument(node)
                if arg_info:
                    arguments.append(arg_info)
            except Exception as e:
                logger.warning(f"Failed to parse argument: {e}")
                raise Exception(f"Failed to parse argument: {e}") from e
    logger.debug(f"\nExtracted arguments:\n{arguments}")
    return arguments


def parse_add_argument(node: ast.Call) -> Dict[str, Any]:
    logger.info(f"\nExtracting arguments from {node}")
    arg_info = {}
    for arg in node.args:
        try:
            if isinstance(arg, ast.Constant) and arg.s.startswith("--"):
                arg_info["name"] = arg.s.replace("-", "_").lower()
        except Exception as e:
            logger.warning(f"Failed to format 'name' argument: {e}")
            raise Exception(f"Failed to format 'name' argument: {e}") from e
        for keyword in node.keywords:
            try:
                if keyword.arg == "type":
                    if isinstance(keyword.value, ast.Name):
                        arg_info["type"] = keyword.value.id
                    elif isinstance(keyword.value, ast.Attribute):
                        arg_info["type"] = (
                            f"{keyword.value.value.id}.{keyword.value.attr}"
                        )
                elif keyword.arg == "default":
                    arg_info["default"] = parse_default_value(keyword.value)
                elif keyword.arg == "help":
                    if isinstance(keyword.value, ast.Constant):
                        arg_info["help"] = keyword.value.s
                elif keyword.arg == "action":
                    if isinstance(keyword.value, ast.Constant):
                        arg_info["action"] = keyword.value.s
            except Exception as e:
                logger.warning(f"Failed to parse argument: {e}")
                raise Exception(f"Failed to parse argument: {e}") from e
        logger.debug(f"\nExtracted argument:\n{arg_info}")
        return arg_info


def find_arguments(document: str) -> List[Dict[str, Any]]:
    logger.info(f"\nExtracting arguments from {document}")
    try:
        # Extract arguments from document1
        args_pattern = re.compile(
            r'parser\.add_argument\(\s*"(.*?)",\s*.*?default\s*=\s*(.*?)\s*[,\)]',
            re.DOTALL,
        )
        logger.debug(f"\nExtracted arguments:\n{args_pattern.findall(document)}")
        return args_pattern.findall(document)
    except Exception as e:
        logger.warning(f"Failed to extract arguments: {e}")
        raise Exception(f"Failed to extract arguments: {e}") from e


def parse_default_value(node: ast.Constant) -> Any:
    logger.info(f"\nExtracting default value from {node}")
    try:
        if isinstance(node, ast.Constant):
            return ast.literal_eval(node)
        return str(ast.unparse(node))
    except Exception as e:
        logger.warning(f"Failed to parse default value: {e}")
        raise Exception(f"Failed to parse default value: {e}") from e


def get_field_type(field: str) -> str:
    logger.info(f"\nGetting field type from {field}")
    try:
        if field == "str":
            return "str"
        elif field == "int":
            return "int"
        elif field == "float":
            return "float"
        elif field == "bool":
            return "bool"
        else:
            return "str"
    except Exception as e:
        logger.warning(f"Failed to get field type: {e}")
        raise Exception(f"Failed to get field type: {e}") from e


def create_nested_models(arguments: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
    logger.info(f"\nCreating nested models")
    nested_structure = {}
    logger.debug(f"\narguments:\n{arguments}")
    for name, argument in arguments.items():
        parts = None
        try:
            if "name" in argument:
                parts = argument["name"].split(".")
            if len(parts) == 1:
                nested_structure[parts[0]] = argument
            elif parts[0] not in nested_structure:
                nested_structure[parts[0]] = {}
                nested_structure[parts[0]][parts[1]] = argument
            else:
                nested_structure[name] = argument
        except Exception as e:
            logger.warning(f"Failed to create nested models: {e}")
            raise Exception(f"Failed to create nested models: {e}") from e
    logger.debug(f"\nnested_structure: {nested_structure}")
    models = {}
    for key, value in nested_structure.items():
        try:
            if isinstance(value, dict):
                fields = {}
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, dict):
                        field_type = get_field_type(subvalue.get("type", "str"))
                        default = subvalue.get("default")
                        description = subvalue.get("help", "")
                        if subvalue.get("action") == "store_true":
                            field_type = bool
                            default = default if default is not None else False
                        fields[subkey] = (
                            field_type,
                            Field(default=default, description=description),
                        )
                    else:
                        fields[subkey] = (
                            ClassVar,
                            Field(default=subvalue, description=None),
                        )

                models[key.capitalize()] = create_model(key.capitalize(), **fields)
            else:
                # Create an empty model for top-level fields
                models[key.capitalize()] = create_model(key.capitalize())
        except Exception as e:
            logger.warning(f"Failed to create nested models: {e}")
            raise Exception(f"Failed to create nested models: {e}") from e
    logger.debug(f"\nnested_structure:\n{nested_structure}")
    return models, nested_structure


def create_environment_string(
    arguments: Dict[str, Any]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    logger.info(f"\nCreating environment string")

    lines = []
    all_arguments = {}

    for argument, value in arguments.items():
        name = None
        default = None
        field_type = None
        help_text = None
        print(argument, value)
        try:
            if isinstance(value, dict):
                if "name" in value:
                    name = value["name"].strip(" ").lower().strip("__")
                else:
                    name = argument
                if "default" in value:
                    default = value["default"]
                    lines.append(f'f"{name}={default}"')
                    if isinstance(default, str):
                        default = default.strip("\n").strip("  ").replace('"', "'")
                if "type" in value:
                    field_type = value["type"].strip("\n").strip("  ")
                if "help" in value:
                    help_text = value["help"].strip("\n").strip("  ")
            elif isinstance(value, str):
                name = argument.strip(" ").lower().strip("__")
                default = value
                field_type = "str"
                help_text = None
                lines.append(f'"{name}={default}"')
            elif isinstance(value, list):
                logger.debug(f"\nvalue: {value}")
                name = argument.strip(" ").lower().strip("__")
                default = value
                field_type = "list"
                help_text = None
                lines.append(f'"{name}={default}"')
            all_arguments[name] = {
                "name": name,
                "default": default,
                "type": field_type,
                "help": help_text,
            }

            logger.debug(f"\nEnvironment string: {lines}")
        except Exception as e:
            logger.warning(f"Failed to create environment string: {e}")
            raise Exception(f"Failed to create environment string: {e}") from e

    return all_arguments, lines


def parse_subnet_folder(file_dir: Union[str, Path]) -> Tuple[Dict[str, Any], List[str]]:
    logger.info(f"\nParsing subnet folder: {file_dir}")
    subnet_arguments = {}
    all_arguments = {}
    for root, dirs, files in os.walk(file_dir):
        for dir in dirs:
            if dir.startswith("__"):
                continue
        try:
            for file in files:

                if file.startswith("__") or file.endswith(".pyc"):
                    continue
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        document = f.read()
                    if "add_argument" not in document:
                        continue
                    file_path = os.path.join(root, file)
                    all_arguments = extract_argparse_arguments(file_path)
                    if len(all_arguments) <= 0:
                        continue
                    logger.debug(f"\nSubnet arguments: {subnet_arguments}")
                    for argument in all_arguments:
                        if not argument:
                            continue
                        if isinstance(argument, dict):
                            if "name" in argument:
                                subnet_arguments[argument["name"]] = argument
                            elif argument is None:
                                continue
                        elif isinstance(argument, list):
                            for argument in all_arguments:
                                if "name" in argument:
                                    subnet_arguments[argument["name"]] = argument
                                    continue
                        if "name" in argument:
                            if argument["name"].startswith("__"):
                                name = (
                                    argument["name"]
                                    .strip(" ")
                                    .lower()
                                    .replace("__", "")
                                )
                                subnet_arguments[name] = argument
                                continue

        except Exception as e:
            logger.warning(f"Failed to parse subnet folder: {e}")
            raise Exception(f"Failed to parse subnet folder: {e}") from e
    logger.debug(f"\nSubnet arguments: {subnet_arguments}")
    all_argmuents, lines = create_environment_string(subnet_arguments)
    lines = list(set(lines))
    logger.debug(f"\nlines:\n{lines}")
    logger.debug(f"\nall_arguments:\n{all_arguments}")
    return all_argmuents, lines


def save_file(file_path: Path, content: str) -> None:
    logger.info(f"\nSaving file: {file_path}")

    try:
        with open(file_path, "w") as f:
            f.write(content)
    except Exception as e:
        logger.warning(f"Failed to save file: {e}")
        raise Exception(f"Failed to save file: {e}") from e


def write_environment_file(
    file_path="module_validator/subnet_modules/bittensor_subnet_template",
    env_file_path=".config.env",
) -> Tuple[List[Dict[str, Any], List[str]]]:
    all_args = parse_subnet_folder(file_path)
    all_arguments = all_args[0]
    env_variables = all_args[1]
    env_keys = []
    for value in env_variables:
        key = value.split('"')[1].split("=")[0]
        value = value.split('"')[1].split("=")[1].split('"')[0]
        if key not in all_arguments.keys():
            all_arguments[key] = value
            env_keys.append(f"f'{key}={value}'")
        env_keys.append(f"f'{key}={value}'")
    save_file(env_file_path, "\n".join(env_keys))
    return all_arguments, env_keys


def write_config_file() -> str:
    final_template = CONFIG_CLASS_TEMPLATE.replace(
        "<<attribute_generation>>", "".join(ATTRIBUTE_LINES)
    )
    final_template = final_template.replace(
        "<<argument_generation>>", "".join(ARGUMENT_LINES)
    )
    final_template = final_template.replace(
        "<<sub_class_generation>>", "".join(CLASS_LINES)
    )
    final_template = final_template.replace(
        "<<environment_generation>>", "".join(ENVIRONMENT_LINES)
    )
    path = Path("config.py")
    path.write_text(final_template)
    return final_template


def parse_attribute_values(
    all_arguments: List[Dict[str, Any]]
) -> Tuple[List[str], List[str], List[str]]:
    classnames = []
    attribute_names = []
    attribute_lines = []
    subclass_lines = {}
    attributename = ""
    fields = ["name", "default", "type", "help", "action"]
    for key, value in all_arguments.items():
        if not key:
            continue
        for field in fields:
            if field not in value.keys():
                value[field] = None
        ARGUMENT_LINES.append(
            COMMAND_LINE_ARG_TEMPLATE.format(
                name=key,
                type=value["type"] or "str",
                default=value["default"] or None,
                help=value["help"] or None,
                action=value["action"] or None,
            )
        )

        if "." in key:
            classname = key.split(".")[0]
            attributename = key.split(".")[1].replace(".", "_")
            full_classname = classname.title() + "Config"
            if full_classname not in classnames:
                classnames.append(full_classname)
                subclass_lines[full_classname] = []
            subclass_lines[full_classname].append(
                ATTRIBUTE_TEMPLATE.format(
                    name=attributename,
                    type=value.get("type", "str"),
                    model_fields=value,
                )
            )
            attribute_names.append(attributename)
            continue
        if attributename not in attribute_names:
            attribute_names.append(key)
            attribute_lines.append(
                ATTRIBUTE_TEMPLATE.format(
                    name=attributename, type=value["type"], model_fields=value
                )
            )
        ATTRIBUTE_LINES.append(
            ATTRIBUTE_TEMPLATE.format(name=key, type=value["type"], model_fields=value)
        )
    return attribute_lines, classnames, subclass_lines


def create_subclass_templates(
    attribute_lines: List[str], classnames: List[str], subclass_lines: List[str]
) -> None:
    ATTRIBUTE_LINES.extend(attribute_lines)
    for classname in classnames:
        sub_class_template = SUB_CLASS_TEMPLATE.format(sub_classname=classname)
        sub_class_template = sub_class_template.replace(
            "<<sub_class_attribute_generation>>", "".join(subclass_lines[classname])
        )
        CLASS_LINES.append(sub_class_template)
        ATTRIBUTE_LINES.append(
            SUBCLASS_ATTRIBUTE_TEMPLATE.format(
                sub_classname=classname.strip("Config").lower(),
                full_classname=classname,
                type=classname,
                model_fields="",
            )
        )


def main() -> str:
    all_arugments, env_keys = write_environment_file()

    for env_key in env_keys:
        ENVIRONMENT_LINES.append(f"            {env_key},\n")

    attribute_lines, classnames, subclass_lines = parse_attribute_values(all_arugments)
    create_subclass_templates(attribute_lines, classnames, subclass_lines)
    return write_config_file()


if __name__ == "__main__":
    main()
