import os
import re
import ast
import sys
import yaml
import json
from typing import Dict, Any, List, ClassVar, Union, Tuple
from pathlib import Path
from pydantic import Field, create_model, BaseModel
from loguru import logger


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
                arg_info["name"] = arg.s.replace(".", "_").replace("-", "_").lower()
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


def find_arguments(document):
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


def parse_default_value(node):
    logger.info(f"\nExtracting default value from {node}")
    try:
        if isinstance(node, ast.Constant):
            return ast.literal_eval(node)
        return str(ast.unparse(node))
    except Exception as e:
        logger.warning(f"Failed to parse default value: {e}")
        raise Exception(f"Failed to parse default value: {e}") from e


def get_field_type(type_str: str):
    logger.info(f"\nExtracting type from {type_str}")
    try:
        type_map = {"str": str, "int": int, "float": float, "bool": bool}
        return type_map.get(type_str, str)
    except Exception as e:
        logger.warning(f"Failed to extract type: {e}")
        raise Exception(f"Failed to extract type: {e}") from e


def create_nested_models(arguments: Dict[str, Any]):
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


def create_argument_string(config_dict: Dict[str, Any]):
    logger.info(f"\nCreating argument string")
    template_lines = []
    default = None
    logger.debug(json.dumps(config_dict, indent=4))
    for key, value in config_dict.items():
        try:
            if "name" in value:
                name = value["name"]
            else:
                name = key
            if isinstance(value, dict):
                for subkey in value.keys():
                    name = f"{key}.{subkey}"
                    default = value["default"]
                    if isinstance(default, str):
                        default = default.replace("'", '"')

                    default = f"""f\"{default}\"""" if "default" in value else "None"
                    field_type = value["type"]
                    help = value["help"]
                    template_lines.append(
                        f"        parser.add_argument('--{name}', type={field_type}, default={default}, help='{help}')\n"
                    )
            else:
                name = key
                default = f'f"\'{default}"' if "default" in value else "None"
                field_type = value["type"]
                help = value["help"]
                template_lines.append(
                    f"        parser.add_argument('--{name}', type={field_type}, default={default}, help='{help}')\n"
                )
        except Exception as e:
            logger.warning(f"Failed to create argument string: {e}")
            raise Exception(f"Failed to create argument string: {e}") from e
    logger.debug(f"\ntemplate_lines:\n{template_lines}")
    template_lines = list(set(template_lines))
    argument_string = "".join(template_lines)
    logger.debug(f"\nargument_string:\n{argument_string}")
    logger.debug(f"\ntemplate_lines:\n{template_lines}")
    return argument_string


def create_config_string(
    models: Dict[str, Any], defaults: Dict[str, Any], classnames: Dict[str, Any]
):
    logger.info(f"\nCreating config string")
    unspecified_types = []
    template_lines = []
    try:
        for classname in classnames:
            if classname.isupper():
                template_lines.append(
                    f"    {classname.lower()}: {classname}Config = Field(default_factory={classname}Config)\n"
                )
    except Exception as e:
        logger.warning(f"Failed to create config string: {e}")

    try:
        for class_name, model in models.items():
            model_dict = model.model_json_schema()
            if "name" in model_dict:
                class_name = model_dict["name"]
                field_type = model_dict["type"]
                field_type = get_field_type(field_type)
                description = model_dict["help"]
                default = model_dict["default"]

                if class_name in defaults:
                    continue
                elif class_name.isupper():
                    template_lines.append(
                        f"    {class_name.lower()}: {field_type} = Field(default={default}, description='{description}')\n"
                    )
                else:
                    template_lines.append(
                        f"    {name.lower().replace('.', '_')}: {field_type} = Field(default={default}, description='{description}')\n"
                    )
            else:
                name = model_dict["title"]
                # default = input(f"Enter value for {name}[No default]: ") or None
                default = None
                if not default:
                    unspecified_types.append(name)
                template_lines.append(
                    f"    {name.lower().replace('.', '_')}: Any = Field(default={default})\n"
                )
    except Exception as e:
        logger.warning(f"Failed to create config string: {e}")
        raise Exception(f"Failed to create config string: {e}") from e
    # template_lines = [line.replace('Any', 'str') for line in template_lines]
    template_lines = list(set(template_lines))
    attribute_template = "".join(template_lines)
    logger.debug(f"\nattribute_template:\n{attribute_template}")
    logger.debug(f"\nunspecified_types:\n{unspecified_types}")
    return attribute_template, unspecified_types


def create_subclass_string(models: str):
    logger.info(f"\nCreating subclass string")
    classnames = []
    defaults = {}
    field_type = None
    template_lines = []
    # attribute_template = "class Config(BaseModel):\n"

    try:
        for class_name, model in models.items():
            if model.__fields__:
                # subclass_template += f"class {class_name}Config(BaseModel):\n"
                classnames.append(class_name)
                for name, field in model.__fields__.items():
                    field_type = get_field_type(field.annotation.__name__)
                    default = (
                        field.default
                        if not isinstance(field.default, type(...))
                        else None
                    )
                    if field_type == str:
                        default = f'"{default}"'.strip("'").strip("\n")
                        defaults[name.lower().replace(".", "_")] = default
                    description = (
                        field.field_info.description
                        if hasattr(field, "field_info")
                        else (
                            field.field_info.help
                            if hasattr(field, "field_info")
                            else f"{class_name}: a {field_type} configuration attribute for {class_name}"
                        )
                    )
                    if description:
                        template_lines.append(
                            f"    {name.lower().strip(' ').replace('.', '_')}: {field_type} = Field(default={default!r}, description={description!r})\n"
                        )
                    else:
                        template_lines.append(
                            f"    {name.lower().strip(' ').replace('.', '_')}: {field_type} = {default!r}\n"
                        )
    except Exception as e:
        logger.warning(f"Failed to create subclass string: {e}")
        raise Exception(f"Failed to create subclass string: {e}") from e

    template_lines.append("\n")

    template_lines = list(set(template_lines))
    subclass_template = "".join(template_lines)
    logger.debug(f"\nsubclass_template:\n{subclass_template}")
    logger.debug(f"\ndefaults:\n{defaults}")
    logger.debug(f"\nclassnames:\n{classnames}")
    return subclass_template, defaults, classnames


def generate_pydantic_model_script(models, output_file: str):
    logger.info(f"\nGenerating pydantic model script: {output_file}")

    pydantic_template = """from pydantic import BaseModel, Field\nfrom typing import Any
from dotenv import load_dotenv
import os

load_dotenv()


{{{sub_class_generation}}}

class Config(GenericConfig):
    def __init__(self, data: Union[BaseModel, Dict[str, Any]]):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        super().__init__(**data)
{{{attribute_generation}}}\n
"""
    # Generate class definitions for nested structures

    subclass_template, defaults, classnames = create_subclass_string(models)

    attribute_template, unspecified_types = create_config_string(
        models, defaults, classnames
    )

    pydantic_template = pydantic_template + subclass_template + attribute_template
    try:
        pydantic_template = pydantic_template.replace(
            "{{{sub_class_generation}}}", subclass_template
        )
        pydantic_template = pydantic_template.replace(
            "{{{attribute_generation}}}", attribute_template
        )
    except Exception as e:
        logger.warning(f"Failed to replace template strings: {e}")
        raise Exception(f"Failed to replace template strings: {e}") from e

    # Add get method to Config class
    pydantic_template += "\n    def get(self, key: str, default: Any = None) -> Any:\n"
    pydantic_template += "        parts = key.split('.')\n"
    pydantic_template += "        value = self\n"
    pydantic_template += "        for part in parts:\n"
    pydantic_template += "            if isinstance(value, BaseModel):\n"
    pydantic_template += "                value = getattr(value, part, default)\n"
    pydantic_template += "            elif isinstance(value, dict):\n"
    pydantic_template += "                value = value.get(part, default)\n"
    pydantic_template += "            else:\n"
    pydantic_template += "                return default\n"
    pydantic_template += "            if value is None:\n"
    pydantic_template += "                return default\n"
    pydantic_template += "   return value\n"

    try:
        with open(output_file, "w") as f:
            f.write(pydantic_template)
    except Exception as e:
        logger.warning(f"Failed to write pydantic model script: {e}")
        raise Exception(f"Failed to write pydantic model script: {e}") from e

    return pydantic_template, subclass_template, attribute_template, unspecified_types


def create_environment_string(arguments):
    logger.info(f"\nCreating environment string")

    lines = []
    all_arguments = {}
    
    for argument, value in arguments.items():
        name=None
        default=None
        field_type=None
        help_text=None
        print(argument, value)
        try:            
            if isinstance(value, dict):
                if "name" in value:
                    name = value["name"].strip(" ").lower().replace(".", "_").strip("__")
                else:
                    name = argument
                if "default" in value:
                    default = value["default"]
                    lines.append(f'f"{name}={default}"')                        
                    if isinstance(default, str):
                        default = default.strip("\n").strip("  ").replace("\"", "\"")
                if "type" in value:
                    field_type = value["type"].strip("\n").strip("  ")
                if "help" in value:
                    help_text = value["help"].strip("\n").strip("  ")
            elif isinstance(value, str):
                name = argument.strip(" ").lower().replace(".", "_").strip("__")
                default = value
                field_type = "str"
                help_text = None
                lines.append(f'"{name}={default}"')
            elif isinstance(value, list):
                logger.debug(f"\nvalue: {value}")
                name = argument.strip(" ").lower().replace(".", "_").strip("__")
                default = value
                field_type = "list"
                help_text = None
                lines.append(f'"{name}={default}"')
            all_arguments[name] = {
                "name": name,
                "default": default,
                "type": field_type,
                "help": help_text
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
                                name = argument["name"].strip(" ").lower().replace("__", "")
                                subnet_arguments[name] = argument
                                continue
                            
                            
                
                              
        except Exception as e:
            logger.warning(f"Failed to parse subnet folder: {e}")
            raise Exception(f"Failed to parse subnet folder: {e}") from e
    logger.debug( f"\nSubnet arguments: {subnet_arguments}" ) 
    all_argmuents, lines = create_environment_string(subnet_arguments)
    lines = list(set(lines))
    logger.debug(f"\nlines:\n{lines}")
    logger.debug(f"\nall_arguments:\n{all_arguments}")
    return all_argmuents, lines


def save_file(file_path: Path, content: str):
    logger.info(f"\nSaving file: {file_path}")

    try:
        with open(file_path, "w") as f:
            f.write(content)
    except Exception as e:
        logger.warning(f"Failed to save file: {e}")
        raise Exception(f"Failed to save file: {e}") from e


def main():
    logger.info(f"\nStarting config generator")

    if len(sys.argv) < 2:
        print("Usage: python config_extractor.py <path_to_config_file>")
        sys.exit(1)

    file_dir = sys.argv[1]
    filename = str(file_dir).split("/")[-1]
    paths_dict = {
        "environment_path": Path(f".{filename}.env"),
        "subnet_env_path": Path(f"module_validator/config/{filename}/.{filename}.env"),
        "configuration_path": Path(
            f"module_validator/config/{filename}/{filename}.yaml"
        ),
        "pydantic_path": Path(
            f"module_validator/config/{filename}/{filename}_configuration.py"
        ),
        "template_path": Path(f"module_validator/config/configuration_template.py"),
        "generated_path": Path(
            f"module_validator/config/{filename}/{filename}_configuration.py"
        ),
    }
    try:
        path_lines = "".join([f"{path}\n" for path in paths_dict.values()])
        with open(paths_dict["template_path"], "r", encoding="utf-8") as f:
            configuration_template = (
                f.read()
                .replace('        """', "")
                .replace('        """', '"""')
                .replace('"""', "")
            )
    except Exception as e:
        logger.warning(f"Failed to read template file: {e}")
        raise Exception(f"Failed to read template file: {e}") from e

    try:
        for path in paths_dict.values():
            path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning(f"Failed to create directory: {e}")
        raise Exception(f"Failed to create directory: {e}") from e

    all_arguments, lines = parse_subnet_folder(file_dir)

    models, nested_structure = create_nested_models(all_arguments)
    logger.debug(f"\nnested_structure: \n{nested_structure}")
    save_file(
        paths_dict["configuration_path"], yaml.safe_dump(nested_structure, indent=2)
    )

    pydantic_template, subclass_template, attribute_template, unspecified_types = (
        generate_pydantic_model_script(models, str(paths_dict["configuration_path"]))
    )

    save_file(paths_dict["pydantic_path"], pydantic_template)

    commandline_arguments = create_argument_string(nested_structure)

    try:
        logger.debug(f"\ncommandline_arguments: \n{commandline_arguments}")
        configuration_template = configuration_template.replace(
            "{{{argument_generation}}}", commandline_arguments
        )
        logger.debug(f"\nsubclass_template: \n{subclass_template}")
        configuration_template = configuration_template.replace(
            "{{{sub_class_generation}}}", subclass_template
        )
        logger.debug(f"\nattribute_template: \n{attribute_template}")
        configuration_template = configuration_template.replace(
            "{{{attribute_generation}}}", attribute_template
        )
        logger.debug(f"\nlines: \n{lines}")
        env_lines = "\n".join(f"""            {env.strip()},""" for env in lines)
        configuration_template = configuration_template.replace(
            "{{{environment_generation}}}", env_lines
        )
    except Exception as e:
        logger.warning(f"Failed to update template file: {e}")
        raise Exception(f"Failed to update template file: {e}") from e

    save_file(paths_dict["generated_path"], configuration_template)

    print(f"Pydantic model with argument prompting has been written to: {path_lines}")

    try:
        unspecified_lines = "".join(
            [
                f"{unspecified_type.lower().strip(' ').replace('.', '_')}\n"
                for unspecified_type in unspecified_types
            ]
        )
    except Exception as e:
        logger.warning(f"Failed to parse subnet folder: {e}")
        raise Exception(f"Failed to parse subnet folder: {e}") from e

    print(
        f"""The following class attributes did not have enough information to configure with proper types for these attributes:
{unspecified_lines}
the class configuration is in {paths_dict['generated_path']}
Correction is recommended but no required.
"""
    )


if __name__ == "__main__":

    main()
