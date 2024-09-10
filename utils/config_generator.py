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


def read_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
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
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(data)
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")


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
    parser.add_argument("--file_dir", help="path the subnet or inference module you are generating a configuration file for")
    parser.add_argument("--config_name", help="bittensor or commune configuration file name", required=False)
    return parser.parse_args()


SUBNET_SOURCE_PATH = Path(parse_args().file_dir)

LIBRARY_NAME = SUBNET_SOURCE_PATH.name
ROOT_PATH = ROOT_PATH = Path("module_validator")
CONFIG_BASE_PATH = ROOT_PATH / "config" 
CONFIG_TEMPLATE_PATH = CONFIG_BASE_PATH / f"{parse_args().config_name}_config_template.py"
MODULE_CONFIG_PATH = CONFIG_BASE_PATH / LIBRARY_NAME 

CONFIG_CLASS_TEMPLATE = read_file(CONFIG_TEMPLATE_PATH)

SUBMODULES_BASE_PATH = ROOT_PATH / "submodules" 
SUBMODULE_BASE_PATH = SUBMODULES_BASE_PATH / LIBRARY_NAME
SUBMODULE_DOTENV_PATH = MODULE_CONFIG_PATH / f".{LIBRARY_NAME}.env"
DOTENV_PATH = f".{LIBRARY_NAME}.env"
YAML_PATH = MODULE_CONFIG_PATH / f"{LIBRARY_NAME}_config.yaml"
SCRIPT_PATH = MODULE_CONFIG_PATH / f"{LIBRARY_NAME}_config.py"

FIELDS = [
    "name",
    "default",
    "action",
    "type",
    "module_fields",
    "help",
    "classname",
    "sub_classname"
]    

    
def extract_argparse_arguments(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    content = read_file(file_path)

    tree = ast.parse(content)
    arguments = []

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument"
        ):
            try:
                if arg_info := parse_add_argument(node):
                    arguments.append(arg_info)
            except Exception as e:
                logger.warning(f"Failed to parse argument: {e}")
# sourcery skip: raise-specific-error
                raise Exception(f"Failed to parse argument: {e}") from e
    return arguments


def parse_add_argument(node: ast.Call) -> Dict[str, Any]:
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
    try:
        if isinstance(node, ast.Constant):
            return ast.literal_eval(node) or str(ast.unparse(node))
    except Exception as e:
        logger.warning(f"Failed to parse default value: {e}")
# sourcery skip: raise-specific-error
        raise Exception(f"Failed to parse default value: {e}") from e


def create_environment_string(
    arguments: Dict[str, Any]
) -> Tuple[List[str], List[Dict[str, Any]]]:
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


# Regex patterns to match command, arguments, and options
COMMAND_PATTERN = re.compile(r"@app\.command\(['\"](\w+[-\w]*)['\"]\)")
ARGUMENT_PATTERN = re.compile(r"(\w+): Annotated\[([^\]]+),\s*typer\.Argument\((.*?)\)\]")
OPTION_PATTERN = re.compile(r"(\w+): Optional\[([^\]]+)\] = typer\.Option\((.*?)\)")

def parse_commands(raw_text: str) -> Dict[str, Any]:
    commands = {}
    
    # Find all command definitions
    command_matches = COMMAND_PATTERN.findall(raw_text)
    for command_match in command_matches:
        command_name = command_match
        commands[command_name] = {"arguments": {}, "options": {}}
        
        # Extract the function related to the command
        func_match = re.search(rf"def (\w+)\((.*?)\):", raw_text, re.DOTALL)
        if func_match:
            name = func_match.group(1)
            body = func_match.group(2)
            
            # Find arguments and options within the function
            argument_matches = ARGUMENT_PATTERN.findall(body)
            for name, arg_type, arg_details in argument_matches:
                commands[command_name]["arguments"][name] = {
                    "type": arg_type.strip(),
                    "help": arg_details.strip()
                }
            
            option_matches = OPTION_PATTERN.findall(body)
            for name, opt_type, opt_details in option_matches:
                commands[command_name]["options"][name] = {
                    "type": opt_type.strip(),
                    "help": opt_details.strip()
                }
    
    return commands

def parse_subnet_folder(file_dir: Union[str, Path]) -> Tuple[Dict[str, Any], List[str]]:
    subnet_arguments = {}
    lines = []
    nested_dict = {}
    classnames = []
    attributenames = []
    classname = ""
    subclass_lines = {}
    for root, dirs, files in os.walk(file_dir):
        for dir in dirs:
            if dir.startswith("__"):
                continue
            if dir.endswith(".pyc"):
                continue
            if dir.endswith(".py"):
                document = read_file(os.path.join(root, dir))
                if "add_argument" not in document:
                    continue
                arguments = extract_argparse_arguments(os.path.join(root, dir))
                for argument in arguments:
                    if not argument or "name" not in argument:
                        continue
                    name = (
                        argument["name"]
                        .strip(" ")
                        .lower()
                        .replace("__", "")
                    )
                    if name not in subnet_arguments:
                        subnet_arguments[name] = argument
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
                    arguments = parse_commands(document)
                    for command, details in arguments.items():
                        name = command.strip(" ").lower().replace("__", "")
                        for arg_name, arg_info in details["arguments"].items():
                            if not arg_name or "name" not in arg_info:
                                continue
                            name = (
                                arg_info["name"]
                                .strip(" ")
                                .lower()
                                .replace("__", "")
                            )
                            subnet_arguments[name] = arg_info
            print(subnet_arguments)
        except Exception as e:
            logger.warning(f"Failed to parse subnet folder: {e}")

    lines = list(set(lines))
    print(json.dumps(lines, indent=4))
    all_argmuents, lines = create_environment_string(subnet_arguments)
    for key, value in all_argmuents.items():
        field_map = {
            "name": value["name"].strip("__") if hasattr(value, "name") else None,
            "default": value["default"] if hasattr(value, "default") else None,
            "type": value["type"] if hasattr(value, "type") else None,
            "help": value["help"] if hasattr(value, "help") else None,
            "action": value["action"] if hasattr(value, "action") else None,
        }
        default = field_map["default"]
        if isinstance(default, str):
            default = default.strip('\n').strip(" ")
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
    write_file(YAML_PATH, yaml.dump(nested_dict, indent=4))
    subclass_lines = {}
    for classname in classnames:
        name = classname
        for attribute_name, values in nested_dict[class_name].items():
            print(attribute_name, values)
            sub_class_template = SUB_CLASS_TEMPLATE.format(sub_classname=classname)
            ATTRIBUTE_LINES.append(SUBCLASS_ATTRIBUTE_TEMPLATE.format(**values))
        SUB_CLASS_LINES.append(sub_class_template.replace("<<sub_class_attribute_generation>>", "".join(subclass_lines[classname])))
        
    attribute_template = "".join(ATTRIBUTE_LINES)
    subclass_template = "".join(SUB_CLASS_LINES)
    environment_template = "".join(ENVIRONMENT_LINES)
    argument_template = "".join(ARGUMENT_LINES)
    config_template = CONFIG_CLASS_TEMPLATE.replace("<<attribute_generation>>", attribute_template).replace("<<sub_class_generation>>", subclass_template).replace("<<environment_generation>>", environment_template).replace("<<argument_generation>>", argument_template)
    write_file(MODULE_CONFIG_PATH / f"{LIBRARY_NAME}_config.py", config_template)
    dotenv_template = "".join(DOTENV_LINES)
    write_file(DOTENV_PATH, dotenv_template)
    write_file(SUBMODULE_DOTENV_PATH, dotenv_template)
    write_file(YAML_PATH, yaml.dump(nested_dict, indent=4))


def main() -> str:    
    parse_subnet_folder(SUBMODULE_BASE_PATH)


if __name__ == "__main__":
    main()