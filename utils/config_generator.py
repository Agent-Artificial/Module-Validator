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
        

CONFIG_CLASS_TEMPLATE = read_file("module_validator/config/configuration_template.py")
SUB_CLASS_TEMPLATE = """
class {full_classname}(GenericConfig):
<<sub_class_attribute_generation>>
    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
        
"""
ATTRIBUTE_TEMPLATE = "    {name}: {type} = Field(name={name}, type={type}, default={default}, description={help})\n"
SUBCLASS_ATTRIBUTE_TEMPLATE = "    {name}: {full_classname} = Field(name={name}, type={type}, default_factory={full_classname})\n"
COMMAND_LINE_ARG_TEMPLATE = "        parser.add_argument('--{name}', name={name}, type={type}, default={default}, description={help})\n"
ENVIRONMENT_TEMPLATE = "        '{env_key}',\n"
DOTENV_TEMPLATE = "{env_key}\n"
SUB_CLASS_LINES = []
CLASS_LINES = []
ENVIRONMENT_LINES = []
ARGUMENT_LINES = []
ATTRIBUTE_LINES = []
DOTENV_LINES = []


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",  help = "path the subnet or inference module you are generating a configuration file for")
    return parser.parse_args()

SUBNET_SOURCE_PATH = Path(parseargs().file)
LIBRARY_NAME = SUBNET_SOURCE_PATH.name
ROOT_PATH = ROOT_PATH = Path("module_validator")
CONFIG_BASE_PATH = ROOT_PATH / "config" / LIBRARY_NAME 
SUBMODULE_BASE_PATH = ROOT_PATH / "submodules" / LIBRARY_NAME 
SUBMODULE_DOTENV_PATH = CONFIG_BASE_PATH / f"{LIBRARY_NAME}.env"
DOTENV_PATH = f"{LIBRARY_NAME}.env"
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
                arg_info["name"] = arg.s.strip("--").lower()
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


def create_nested_models(arguments: Dict[str, Any], env_list: List[str]) -> Tuple[List[str], Dict[str, Any]]:

    """
    Creates nested models based on the arguments.

    Args:
        arguments (Dict[str, Any]): The arguments to create the models from.

    Returns:
        Tuple[List[str], Dict[str, Any]]: The created models and the nested structure.
    """
    
    nested_structure = {}
    # Create nested models
    for name, argument in arguments.items():
        parts = None
        try:
            if "name" in argument:
                # Extract the name of the argument from the dot(.) in the argument.name
                parts = argument["name"].split(".")
            if len(parts) == 1:
                nested_structure[parts[0]] = argument
            elif parts[0] not in nested_structure:
                nested_structure[parts[0]] = {parts[1]: argument}
            else:
                nested_structure[name] = argument
        except Exception as e:
            logger.warning(f"Failed to create nested models: {e}")
# sourcery skip: low-code-quality, raise-specific-error
            raise Exception(f"Failed to create nested models: {e}") from e
    models = {}
    # Handle the nested subclasses
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
# sourcery skip: raise-specific-error
            raise Exception(f"Failed to create nested models: {e}") from e
    for environment_string in env_list:
        name, default = environment_string.split("=", 1)
        name = name.replace(".", "_")
        if name in models:
            nested_structure[name] =  default
    write_file(YAML_PATH, yaml.dump(nested_structure))    
    return models, nested_structure

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
        field_type = None
        help_text = None
        try:
            if isinstance(value, dict):
                if "name" in value:
                    name = value["name"].strip(" ").lower().strip("__")
                else:
                    name = argument
                if "default" in value:
                    default = value["default"]
                    lines.append(f'{name}={default}')
                    if isinstance(default, str):
                        default = default.strip("\n").strip("  ").replace("'", '"')
                if "type" in value:
                    field_type = value["type"].strip("\n").strip("  ")
                if "help" in value:
                    help_text = value["help"].strip("\n").strip("  ")
            elif isinstance(value, str):
                name = argument.strip(" ").lower().strip("__")
                default = value
                field_type = "str"
                help_text = None
                lines.append(f'{name}={default}')
            elif isinstance(value, list):
                name = argument.strip(" ").lower().strip("__")
                default = value
                field_type = "list"
                help_text = None
                lines.append(f'{name}={default}')
            all_arguments[name] = {
                "name": name,
                "default": default,
                "type": field_type,
                "help": help_text,
            }

        except Exception as e:
            logger.warning(f"Failed to create environment string: {e}")
# sourcery skip: raise-specific-error
            raise Exception(f"Failed to create environment string: {e}") from e

    return all_arguments, lines




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
    environment_lines = "".join(list(set(ENVIRONMENT_LINES)))
    dotenv_lines = "".join(list(set(DOTENV_LINES)))
    write_file(DOTENV_PATH, dotenv_lines)
    write_file(SUBMODULE_DOTENV_PATH, environment_lines)

    argument_template = ''.join(list(set(ARGUMENT_LINES)))
    attribute_template = "".join(list(set(ATTRIBUTE_LINES)))
    class_template = "".join(list(set(CLASS_LINES)))
    print(class_template)
    environment_template = "".join(list(set(ENVIRONMENT_LINES)))
    final_template = CONFIG_CLASS_TEMPLATE.replace(
        "<<attribute_generation>>",
        attribute_template
    )
    final_template = final_template.replace(
        "<<argument_generation>>",
        argument_template
    )
    final_template = final_template.replace(
        "<<sub_class_generation>>",
        class_template
    )
    final_template = final_template.replace(
        "<<environment_generation>>", 
        environment_template
    )
    write_file(SCRIPT_PATH, final_template)
    return final_template


def print_lines(key, value):
    lines = [
        f"Argument:       {key}",
        f"Description:    {value['help']}",
        f"Default:        {value['default']}",
        f"Enter value for {key}: ",
    ]
    print('\n'.join(lines))

def parse_attribute_values(
    all_arguments: List[Dict[str, Any]],
    lines: List[str]
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
    argument_names = []
    argument_lines = []
    
    attribute_names = []
    attribute_lines = []
    
    class_lines = []
    classnames = []
    subclass_lines = {}
    
    environment_lines = []
    dotenv_lines = []
    environment_names = []
    
        
    for key, value in all_arguments.items():
        if not key:
            continue
        classname = ""
        attributename = ""
        full_classname = ""
        print(value)
        if isinstance(value, dict):
            if key == "config":
                continue
            if not hasattr(value, "name"):
                value["name"] = key
            if not hasattr(value, "default"):
                value["default"] = None
            if not hasattr(value, "type"):
                value["type"] = "str"
            if not hasattr(value, "description"):
                value["description"] = f"Argument for {value['name']}"
            print_lines(key, value)
            default = input()
            value["default"] = default
        
        elif "." in key:
            classname = key.split(".")[0]
            attributename = key.split(".")[1]
            full_classname = f"{classname.title()}Config"
            if full_classname not in classnames:
                classnames.append(full_classname)
                subclass_lines[full_classname] = [
                    ATTRIBUTE_TEMPLATE.format(
                        name=attributename,
                        type=value.get("type", "str"),
                        default=f"'{value['default']}'",
                        help=f"'{value['help']}'"
                    )
                ]
        if key not in attribute_names and "." not in key:
            attribute_lines.append(
                ATTRIBUTE_TEMPLATE.format(
                    name=key,
                    type=value.get("type", "str"),
                    default=f"'{value['default']}'",
                    help=f"'{value['help']}'"
                )
            )
            attribute_names.append(key)
        if key not in environment_names:
            env_line = f"{key.lower().replace('.', '_')}={value['default']}"
            
            environment_lines.append(
                ENVIRONMENT_TEMPLATE.format(
                    env_key=env_line
                )
            )
            dotenv_lines.append(
                DOTENV_TEMPLATE.format(
                    env_key=env_line
                )
            )
            environment_names.append(key)
    
        if key not in argument_names:
            argument_lines.append(COMMAND_LINE_ARG_TEMPLATE.format(
                name=key,
                type=value.get("type", "str"),
                default=f"'{value['default']}'",
                help=f"'{value['help']}'"
            ))
            argument_names.append(key)
            
                                                     
    for key in classnames:
        
        class_lines.append(SUBCLASS_ATTRIBUTE_TEMPLATE.format(
            name = key.lower().replace(".", "_").strip("Config"),
            full_classname=key,
        ))
        
        lines = "".join(subclass_lines[key])
        class_template = SUB_CLASS_TEMPLATE.format(
            full_classname=key,
        )
        class_template.replace("<<sub_class_attribute_generation>>", lines)
        CLASS_LINES.append(class_template)
    
    ATTRIBUTE_LINES.extend(attribute_lines)
    ARGUMENT_LINES.extend(argument_lines)
    ENVIRONMENT_LINES.extend(environment_lines)
    DOTENV_LINES.extend(dotenv_lines)
    print(f"""
{"".join(ATTRIBUTE_LINES)}
{"".join(ARGUMENT_LINES)}
{"".join(ENVIRONMENT_LINES)}
{"".join(DOTENV_LINES)}
""")
    create_subclass_templates(ATTRIBUTE_LINES, classnames, class_lines)
    subclass_dict = {}
    for key, value in all_arguments.items():
        if "." not in key:
            subclass_dict[key] = value
        else:
            keys = key.split(".")
            subclass_dict[keys[0]] = {keys[1]: value["default"]}
    write_file(YAML_PATH, yaml.dump(subclass_dict, indent=4))
    write_config_file()


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
        sub_class_template = SUB_CLASS_TEMPLATE.format(full_classname=classname)
        sub_class_template = sub_class_template.replace(
            "<<sub_class_attribute_generation>>", "".join(subclass_lines[classname])
        )
        CLASS_LINES.append(sub_class_template)
        ATTRIBUTE_LINES.append(
            SUBCLASS_ATTRIBUTE_TEMPLATE.format(
                name=classname.strip("Config").lower(),
                type=classname,
                full_classname=classname,
                default_factory=classname                
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
                        all_arguments.add(name)
        except Exception as e:
            logger.warning(f"Failed to parse subnet folder: {e}")
    all_argmuents, lines = create_environment_string(subnet_arguments)
    lines = list(set(lines))
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

    file_dir = parseargs().file
    all_arguments, lines = parse_subnet_folder(file_dir)
    parse_attribute_values(all_arguments, lines)
    return create_nested_models(all_arguments)


if __name__ == "__main__":
    main()
