import re
import os
import ast
import yaml
import json
import argparse
from typing import Dict, Any, List, ClassVar, Union, Tuple, Optional
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
ATTRIBUTE_TEMPLATE = """    {name}: {type} = Field(name="{name}", type={type}, default={default}, help="{help}", action={action})\n"""
SUBCLASS_ATTRIBUTE_TEMPLATE = "    {name}: {type} = Field(default_factory={type}, type={type}, help='{help}', action={action})\n"
COMMAND_LINE_ARG_TEMPLATE = '        parser.add_argument("--{name}", default={default}, type={type}, help="{help}", action={action})\n'
ENVIRONMENT_TEMPLATE = "        '{env_lines}',\n"
DOTENV_TEMPLATE = "{env_lines}\n"
SUB_CLASS_LINES = []
CLASS_LINES = []
ENVIRONMENT_LINES = []
ARGUMENT_LINES = []
ATTRIBUTE_LINES = []
DOTENV_LINES = []


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_dir",  help = "path the subnet or inference module you are generating a configuration file for")
    return parser.parse_args()

SUBNET_SOURCE_PATH = Path(parse_args().file_dir)
LIBRARY_NAME = SUBNET_SOURCE_PATH.name
ROOT_PATH = ROOT_PATH = Path("module_validator")
CONFIG_BASE_PATH = ROOT_PATH / "config" / LIBRARY_NAME 
SUBMODULE_BASE_PATH = ROOT_PATH / "submodules" / LIBRARY_NAME 
SUBMODULE_DOTENV_PATH = CONFIG_BASE_PATH / f".{LIBRARY_NAME}.env"
DOTENV_PATH = f".{LIBRARY_NAME}.env"
YAML_PATH = CONFIG_BASE_PATH / f"{LIBRARY_NAME}_config.yaml"
SCRIPT_PATH = CONFIG_BASE_PATH / f"{LIBRARY_NAME}_config.py"

FIELDS = ["name", "default", "action", "type", "module_fields", "help", "classname", "sub_classname"]    

    
def extract_argparse_arguments(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Extracts argparse arguments from a given file.

    Args:
        file_path (str): Path to the file containing argparse arguments.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries where each dictionary represents an argument.
            Each dictionary contains the following information:
                - name (str): The name of the argument.
                - type (str): The type of the argument.
                - default (str): The default value of the argument.
                - help (str): The help string of the argument.
                - action (str): The action of the argument.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    logger.info(f"\nExtracting arguments from {file_path}")
    content = read_file(file_path)

    tree = ast.parse(content)
    arguments = []

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument"
        ):
            try:
                if arg_info := parse_add_argument(node):
                    arguments.append(arg_info)
            except Exception as e:
                logger.warning(f"Failed to parse argument: {e}")
# sourcery skip: raise-specific-error
                raise Exception(f"Failed to parse argument: {e}") from e
    logger.debug(f"\nExtracted arguments:\n{arguments}")
    return arguments


def parse_add_argument(node: ast.Call) -> Dict[str, Any]:
    """
    Extracts information about a single argparse argument from a given node.

    Args:
        node (ast.Call): The ast node representing the argparse argument.

    Returns:
        Dict[str, Any]: A dictionary containing the following information:
            - name (str): The name of the argument.
            - type (str): The type of the argument.
            - default (str): The default value of the argument.
            - help (str): The help string of the argument.
            - action (str): The action of the argument.
    """
    arg_info = {}
    for arg in node.args:
        try:
            if isinstance(arg, ast.Constant) and arg.s.startswith("--"):
                arg_info["name"] = arg.s.replace("-", "_").lower()
        except Exception as e:
            logger.warning(f"Failed to format 'name' argument: {e}")
# sourcery skip: raise-specific-error
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
# sourcery skip: raise-specific-error
                raise Exception(f"Failed to parse argument: {e}") from e
        return arg_info


def find_arguments(document: str) -> List[Dict[str, Any]]:
    """
    Extracts argparse arguments from a given document.

    Args:
        document (str): The document containing argparse arguments.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries where each dictionary represents an argument.
            Each dictionary contains the following information:
                - name (str): The name of the argument.
                - default (str): The default value of the argument.
    """
    try:
        # Extract arguments from document1
        args_pattern = re.compile(
            r'parser\.add_argument\(\s*"(.*?)",\s*.*?default\s*=\s*(.*?)\s*[,\)]',
            re.DOTALL,
        )
        return args_pattern.findall(document)
    except Exception as e:
        logger.warning(f"Failed to extract arguments: {e}")
# sourcery skip: raise-specific-error
        raise Exception(f"Failed to extract arguments: {e}") from e


def parse_default_value(node: ast.Constant) -> Any:
    
    """
    Extracts the default value from an ast node.

    Args:
        node (ast.Constant): The node from which to extract the default value.

    Returns:
        Any: The default value.
    """
    try:
        if isinstance(node, ast.Constant):
            return ast.literal_eval(node) or str(ast.unparse(node))
    except Exception as e:
        logger.warning(f"Failed to parse default value: {e}")
# sourcery skip: raise-specific-error
        raise Exception(f"Failed to parse default value: {e}") from e


def get_field_type(field: str) -> str:
    """
    Converts a field type string to a Python type string.

    Args:
        field (str): The field type string.

    Returns:
        str: The Python type string.
    """
    try:
        if field == "bool":
            return "bool"
        elif field == "float":
            return "float"
        elif field == "int":
            return "int"
        else:
            return "str"
    except Exception as e:
        logger.warning(f"Failed to get field type: {e}")
# sourcery skip: raise-specific-error
        raise Exception(f"Failed to get field type: {e}") from e



def create_environment_string(
    arguments: Dict[str, Any]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Creates an environment string based on the arguments.

    Args:
        arguments (Dict[str, Any]): The arguments to create the environment string from.

    Returns:
        Tuple[List[str], List[Dict[str, Any]]]: The created environment string and the nested structure.
    """
    logger.info("\nCreating environment string")

    lines = []
    all_arguments = {}

    for argument, value in arguments.items():
        name = None
        default = None
        type = None
        help = None
        try:
            if isinstance(value, dict):
                if "name" in value:
                    name = value["name"].strip(" ").lower().strip("__")
                else:
                    name = argument
                if "default" in value:
                    default = value["default"]
                    lines.append(f"{name}={default}")
                    if isinstance(default, str):
                        default = default.strip('\n').strip('  ')

                if "type" in value:
                    type = value["type"].strip("\n").strip("  ")
                if "help" in value:
                    help = value["help"].strip("\n").strip("  ")
            elif isinstance(value, str):
                name = argument.strip(" ").lower().strip("__")
                default = value
                if "os.getenv" in default:
                    default = f"f'\'{default}'\'"
                type = "str"
                help = None
                lines.append(f"{name}={default}")
            elif isinstance(value, list):
                logger.debug(f"\nvalue: {value}")
                name = argument.strip(" ").lower().strip("__")
                default = value
                type = "list"
                help = None
                lines.append(f"{name}={default}")
            if isinstance(value["default"], str):
                default = f'{default}'
            all_arguments[name] = {
                "name": name,
                "default": default or None,
                "type": type,
                "help": help,
            }

        except Exception as e:
            logger.warning(f"Failed to create environment string: {e}")
# sourcery skip: raise-specific-error
            raise Exception(f"Failed to create environment string: {e}") from e
        logger.warning(f"failed to create environment string:\n{argument}\n{value}")
    return all_arguments, lines


def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path: Union[str, Path], data: str):
    if isinstance(file_path, str):
        file_path = Path(file_path)
    try:
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(data)
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")



def write_environment_file(
    file_path=SUBNET_SOURCE_PATH,
    env_file_path=DOTENV_PATH,
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Generate and save environment variables from a specified subnet folder. 
    This function parses the subnet folder to extract arguments and environment variables, 
    then saves them to a specified environment file.

    Args:
        file_path (str): The path to the subnet folder to parse. Defaults to 
            "module_validator/subnet_modules/bittensor_subnet_template".
        env_file_path (str): The path where the environment file will be saved. 
            Defaults to ".config.env".

    Returns:
        Tuple[List[Dict[str, Any]], List[str]]: A tuple containing a dictionary of 
        all arguments and a list of environment variable strings.

    Examples:
        >>> write_environment_file()
        >>> write_environment_file("path/to/subnet", "path/to/env_file")
    """

    all_arguments, env_variables = parse_subnet_folder(file_path)
    env_keys = []
    for value in env_variables:
        key = value.split('"')[1].split("=")[0].replace(" ", "")
        value = value.split('"')[1].split("=")[1].split('"')[0]
        if key not in all_arguments.keys():
            all_arguments[key] = value
            env_keys.append(f"{key}={value}")
        env_keys.append(f"{key}={value}")
        write_file(DOTENV_PATH, "\n".join(env_keys))
        write_file(SUBMODULE_DOTENV_PATH, "\n".join(env_keys))
    return all_arguments, env_keys


def write_config_file() -> str:
    """
    Generate a configuration file by populating a template with specified lines. 
    This function replaces placeholders in a configuration class template with 
    actual content and writes the final configuration to a file.

    Returns:
        str: The final configuration template as a string.

    Examples:
        >>> config_content = write_config_file()
    """

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
    write_file(SCRIPT_PATH, final_template)
    return final_template


def parse_attribute_values(
    all_arguments: List[Dict[str, Any]]
) -> Tuple[List[str], List[str], List[str]]:
    """
    Extract and format attribute values from a list of argument dictionaries. 
    This function processes the provided arguments to generate attribute lines, 
    class names, and subclass lines for configuration purposes.

    Args:
        all_arguments (List[Dict[str, Any]]): A list of dictionaries containing 
            argument details, including name, default value, type, help text, 
            and action.

    Returns:
        Tuple[List[str], List[str], List[str]]: A tuple containing:
            - A list of formatted attribute lines.
            - A list of class names derived from the arguments.
            - A dictionary mapping class names to their corresponding attribute lines.

    Examples:
        >>> attribute_lines, classnames, subclass_lines = parse_attribute_values(arguments)
    """
    
    classnames = []
    attribute_names = []
    attribute_lines = []
    subclass_lines = {}
    class_dict = {}
    attributename = ""
    fields = ["name", "default", "type", "help", "action"]
    for key, value in all_arguments.items():
        if not key:
            continue
        for field in fields:
            if field not in value.keys():
                value[field] = None
                help = value["help"]
                if isinstance(help, str):
                    value["help"] = help.replace('"', "'")
        if isinstance(value["default"], int):
            value["type"] = "int"
        if value["type"] == "str":
            if value["default"] is None:
                value["default"] = ""

            if "os.getenv" in value["default"]:
                value["default"] = f"\f'{value['default']}\'"
            value["default"] = f'"{value["default"]}"'
        ARGUMENT_LINES.append(
            COMMAND_LINE_ARG_TEMPLATE.format(
                name=key.replace(".", "_"),
                type=value["type"] or "str",
                default=value["default"] or None,
                help=value["help"] or None,
                action=value["action"] or None,
            )
        )

        if "." in key:
            classname = key.split(".")[0]
            attributename = key.split(".")[1]
            full_classname = f"{classname.title()}Config"
            if full_classname not in classnames:
                classnames.append(full_classname)
                subclass_lines[full_classname] = []
            if attributename:
                value["name"] = attributename
            class_dict[full_classname] = {attributename: value["default"]}
            subclass_lines[full_classname].append(
                ATTRIBUTE_TEMPLATE.format(
                    name=value["name"] or attributename,
                    type=value["type"] or "str",
                    default=value["default"] or None,
                    help=value["help"] or None,
                    action=value["action"] or None,
                )
            )
            attribute_names.append(attributename)
            continue
        else:
            class_dict[key] = value

        if attributename not in attribute_names:
            attribute_names.append(key)
            attribute_lines.append(
                ATTRIBUTE_TEMPLATE.format(
                    name=value["name"] or key.replace(".", "_").lower(),
                    type=value["type"] or "str",
                    default=value["default"] or None,
                    help=value["help"] or None,
                    action=value["action"] or None,
                )
            )

        ATTRIBUTE_LINES.append(
            ATTRIBUTE_TEMPLATE.format(
                **value
            )
        )

    return attribute_lines, classnames, subclass_lines


def create_subclass_templates(
    attribute_lines: List[str], classnames: List[str], subclass_lines: List[str]
) -> None:
    """
    Generate and append subclass templates based on provided attribute lines and class names. 
    This function constructs subclass templates and updates global lists with the generated 
    class and attribute information.

    Args:
        attribute_lines (List[str]): A list of formatted attribute lines to be added.
        classnames (List[str]): A list of class names for which subclasses will be created.
        subclass_lines (List[str]): A dictionary mapping class names to their corresponding 
            attribute lines.

    Returns:
        None

    Examples:
        >>> create_subclass_templates(attribute_lines, classnames, subclass_lines)
    """
    ATTRIBUTE_LINES.extend(attribute_lines)
    for classname in classnames:
        sub_class_template = SUB_CLASS_TEMPLATE.format(sub_classname=classname)
        sub_class_template = sub_class_template.replace(
            "<<sub_class_attribute_generation>>", "".join(subclass_lines[classname])
        )
        CLASS_LINES.append(sub_class_template)
        ATTRIBUTE_LINES.append(
            SUBCLASS_ATTRIBUTE_TEMPLATE.format(
                name=classname.lower(),
                type=classname,   
                help=None,   
                action=None         
            )
        )


def parse_subnet_folder(file_dir: Union[str, Path]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Parses a subnet folder and extracts argparse arguments from all python files in the folder.

    Args:
        file_dir (Union[str, Path]): The path to the subnet folder.

    Returns:
        Tuple[Dict[str, Any], List[str]]: A dictionary of all arguments and a list of lines for the environment string.
    """
    logger.info(f"\nParsing subnet folder: {file_dir}")
    subnet_arguments = {}
    all_arguments = set()
    nested_dict = {}
    classnames = []
    attributenames = []
    classname = ""
    subclass_lines = {}
    for root, dirs, files in os.walk(file_dir):
        for dir in dirs:
            if dir.startswith("__"):
                continue
        try:
            for file in files:
                if file.startswith("__") or file.endswith(".pyc"):
                    continue
                if file.endswith(".py"):
                    document = read_file(os.path.join(root, file))
                    if "add_argument" not in document:
                        continue
                    arguments = extract_argparse_arguments(os.path.join(root, file))
                    for argument in arguments:
                        if not argument or "name" not in argument:
                            continue
                        name = (
                            argument["name"]
                            .strip(" ")
                            .lower()
                            .replace("__", "")
                        )

                        subnet_arguments[name] = argument
                        continue
                    all_arguments.add(name)
            all_argmuents, lines = create_environment_string(subnet_arguments)
        except Exception as e:
            logger.warning(f"Failed to parse subnet folder: {e}")

    lines = list(set(lines))
    print(json.dumps(lines, indent=4))

    for key, value in subnet_arguments.items():
        field_map = {
            "name": value["name"].strip("__") if hasattr(value, "name") else None,
            "default": value["default"] if hasattr(value, "default") else None,
            "type": value["type"] if hasattr(value, "type") else None,
            "help": value["help"] if hasattr(value, "help") else None,
            "action": value["action"] if hasattr(value, "action") else None,
        }
        default = field_map["default"]
        if isinstance(default, str):
            default = default.strip('\\n').strip(" ")
            if default.startswith("os.get"):
                field_map["default"] = f"f'{default}'"
            else: 
                field_map["default"] = f"'{default}'"
        if isinstance(default, int):
            field_map["type"] = "str"

        if "." in key:
            class_name, attribute_name = key.split(".")
            if classname not in nested_dict:
                class_name = f'{classname}Config'
                nested_dict[class_name] = {}
                
            nested_dict[class_name][attribute_name] = field_map
            subclass_lines[classname] = [SUBCLASS_ATTRIBUTE_TEMPLATE.format(**field_map)]
            attributenames.append(attribute_name)

        else:
            attribute_name = key
            nested_dict[attribute_name] = field_map


        env_line = f'{name}={default}'
        ENVIRONMENT_LINES.append(f"            \'{env_line}\'\n")
        DOTENV_LINES.append(f"{env_line}\n")
    write_file(YAML_PATH, yaml.dump(nested_dict))
    subclass_lines = {}
    for classname in classnames:
        name = classname
        for attribute_name, values in nested_dict[class_name].items():
            print(attribute_name, values)
            SUB_CLASS_LINES.append()
        sub_class_template = SUB_CLASS_TEMPLATE.format(sub_classname=classname)
        
        


    ENVIRONMENT_TEMPLATE = "".join(ENVIRONMENT_LINES)
    DOTENV_TEMPLATE = "".join(DOTENV_LINES)
    write_file(DOTENV_PATH, DOTENV_TEMPLATE)
    write_file(SUBMODULE_DOTENV_PATH, DOTENV_TEMPLATE)

    print(json.dumps(classnames, indent=4))
    print(json.dumps(attributenames, indent=4))
    print(json.dumps(nested_dict, indent=4))
    return all_argmuents, lines


def main() -> str:
    """
    Orchestrate the generation of environment variables, attribute values, and configuration files. 
    This function coordinates the workflow by writing environment files, parsing attribute values, 
    creating subclass templates, and finally writing the configuration file.

    Returns:
        str: The content of the generated configuration file.

    Examples:
        >>> config_content = main()
    """
    file_dir = parse_args().file_dir
    all_arguments, env_lines = parse_subnet_folder(file_dir)

    for line in env_lines:
        line=line.replace(".", "_")
        ENVIRONMENT_LINES.append(ENVIRONMENT_TEMPLATE.format(env_lines=line))
        DOTENV_LINES.append(DOTENV_TEMPLATE.format(env_lines=line))
    
    write_file(DOTENV_PATH, ''.join(DOTENV_LINES))
    write_file(SUBMODULE_DOTENV_PATH, ''.join(DOTENV_LINES))
    attribute_lines, classnames, subclass_lines = parse_attribute_values(all_arguments)
    create_subclass_templates(attribute_lines, classnames, subclass_lines)
    return write_config_file()


if __name__ == "__main__":
    main()
