import os
import re
import ast
import sys
import yaml
import json
from typing import Dict, Any, List, ClassVar, Union, Tuple
from pathlib import Path
from pydantic import Field, create_model, BaseModel


def extract_argparse_arguments(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r') as file:
        content = file.read()

    tree = ast.parse(content)
    arguments = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument':
            arg_info = parse_add_argument(node)
            if arg_info:
                arguments.append(arg_info)

    return arguments


def parse_add_argument(node: ast.Call) -> Dict[str, Any]:
    arg_info = {}
    for arg in node.args:
        if isinstance(arg, ast.Constant) and arg.s.startswith('--'):
            arg_info['name'] = arg.s.lstrip('-').replace('.', "_").replace("-", "_").lower()
    for keyword in node.keywords:
        if keyword.arg == 'type':
            if isinstance(keyword.value, ast.Name):
                arg_info['type'] = keyword.value.id
            elif isinstance(keyword.value, ast.Attribute):
                arg_info['type'] = f"{keyword.value.value.id}.{keyword.value.attr}"
        elif keyword.arg == 'default':
            arg_info['default'] = parse_default_value(keyword.value)
        elif keyword.arg == 'help':
            if isinstance(keyword.value, ast.Constant):
                arg_info['help'] = keyword.value.s
        elif keyword.arg == 'action':
            if isinstance(keyword.value, ast.Constant):
                arg_info['action'] = keyword.value.s
    return arg_info


def find_arguments(document):
    # Extract arguments from document1
    args_pattern = re.compile(r'parser\.add_argument\(\s*"(.*?)",\s*.*?default\s*=\s*(.*?)\s*[,\)]', re.DOTALL)
    return args_pattern.findall(document)


def parse_default_value(node):
    if isinstance(node, ast.Constant):
        return ast.literal_eval(node)
    return str(ast.unparse(node))


def get_field_type(type_str: str):
    type_map = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool
    }
    return type_map.get(type_str, str)
    

def create_nested_models(arguments: Dict[str, Any]):
    nested_structure = {}
    for name, argument in arguments.items():
        parts = None
        if "name" in argument:
            parts = argument['name'].split('.')
        if len(parts) == 1:
            nested_structure[parts[0]] = argument
        elif parts[0] not in nested_structure:
            nested_structure[parts[0]] = {}
            nested_structure[parts[0]][parts[1]] = argument
        else:
            nested_structure[name] = argument

    
    models = {}
    for key, value in nested_structure.items():
        if isinstance(value, dict):
            fields = {}
            for subkey, subvalue in value.items():
                if isinstance(subvalue, dict):
                    field_type = get_field_type(subvalue.get('type', 'str'))
                    default = subvalue.get('default')
                    description = subvalue.get('help', '')
                    if subvalue.get('action') == 'store_true':
                        field_type = bool
                        default = default if default is not None else False
                    fields[subkey] = (field_type, Field(default=default, description=description))
                else:
                    fields[subkey] = (ClassVar, Field(default=subvalue, description=None))
                    
            models[key.capitalize()] = create_model(key.capitalize(), **fields)
        else:
            # Create an empty model for top-level fields
            models[key.capitalize()] = create_model(key.capitalize())

    return models, nested_structure

def create_argument_string(config_dict: Dict[str, Any]):
    template_lines = []
    default = None
    skip_values = ("type", "default", "help")
    for key, value in config_dict.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                [name, default, field_type, help] = [None] * 4
                if "name" in value:
                    name = value["name"]
            if "default" in value:
                default = value["default"]
                if isinstance(default, str):
                    default = default.replace("'", '"').strip()
            if "type" in value:
                field_type = value["type"]
            if "help" in value:
                help = value["help"]
            template_lines.append(f"        parser.add_argument('--{name}', type={field_type}, default={default}, help='{help}')\n")
        
            for subkey in value.keys():
                name = f"{key}.{subkey}"
                default = value["default"]
                if isinstance(default, str):
                    default = default.replace("'", '"')
                default = f"""f\"'{default}'\"""" if "default" in value else "None"
                field_type = value["type"]
                help = value["help"]
                template_lines.append(f"        parser.add_argument('--{name}', type={field_type}, default={default}, help='{help}')\n")
        else:
            name = key
            default = f"f\"'{default}'\"" if "default" in value else "None"
            field_type = value["type"]
            help = value["help"]
            template_lines.append(f"        parser.add_argument('--{name}', type={field_type}, default={default}, help='{help}')\n")
        print(key, value)
    template_lines = list(set(template_lines))
    argument_string = "".join(template_lines)
    return argument_string

def create_config_string(models: Dict[str, Any], defaults: Dict[str, Any], classnames: Dict[str, Any]):
    unspecified_types = []
    template_lines = []
    for classname in classnames:
        if classname.isupper():
            template_lines.append(f"    {classname.lower()}: {classname}Config = Field(default_factory={classname}Config)\n")
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
                template_lines.append(f"    {class_name.lower()}: {field_type} = Field(default={default}, description='{description}')\n")
            else:
                template_lines.append(f"    {name.lower().replace('.', '_')}: {field_type} = Field(default={default}, description='{description}')\n")
        else:
            name = model_dict["title"]
            # default = input(f"Enter value for {name}[No default]: ") or None
            default = None
            if not default:
                unspecified_types.append(name)
            template_lines.append(f"    {name.lower().replace('.', '_')}: Any = Field(default={default})\n")

    template_lines = list(set(template_lines))
    attribute_template = "".join(template_lines)
    return attribute_template, unspecified_types

def create_subclass_string(models: str):
    classnames = []
    defaults = {}
    field_type = None
    template_lines = []
    # attribute_template = "class Config(BaseModel):\n"
    
    for class_name, model in models.items():
        if model.__fields__:
            # subclass_template += f"class {class_name}Config(BaseModel):\n"
            classnames.append(class_name)
            for name, field in model.__fields__.items():
                field_type = get_field_type(field.annotation.__name__)
                default = field.default if not isinstance(field.default, type(...)) else None
                if field_type == str:
                    default = f'"{default}"'.strip("'").strip("\n")
                    defaults[name.lower().replace('.', '_')] = default
                description = field.field_info.description if hasattr(field, 'field_info') else field.field_info.help if hasattr(field, 'field_info') else f"{class_name}: a {field_type} configuration attribute for {class_name}"
                if description:
                    template_lines.append(f"    {name.lower().strip(' ').replace('.', '_')}: {field_type} = Field(default={default!r}, description={description!r})\n")
                else:
                    template_lines.append(f"    {name.lower().strip(' ').replace('.', '_')}: {field_type} = {default!r}\n")
    template_lines.append("\n")
    
    template_lines = list(set(template_lines))
    subclass_template = "".join(template_lines)

    return subclass_template, defaults, classnames

                
def generate_pydantic_model_script(models, output_file: str):
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
    
    attribute_template, unspecified_types = create_config_string(models, defaults, classnames)
                            
    pydantic_template = pydantic_template + subclass_template + attribute_template
    pydantic_template = pydantic_template.replace("{{{sub_class_generation}}}", subclass_template)
    pydantic_template = pydantic_template.replace("{{{attribute_generation}}}", attribute_template)
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
    pydantic_template += "        return value\n"
 
    with open(output_file, 'w') as f:
        f.write(pydantic_template)
    return pydantic_template, subclass_template, attribute_template, unspecified_types


def parse_subnet_folder(file_dir: Union[str, Path]) -> Tuple[Dict[str, Any], List[str]]:
    lines = []
    all_arguments = {}
    for root, dirs, files in os.walk(file_dir):
        for dir in dirs:
            if dir.startswith("__"):
                continue
        for file in files:
            if file.startswith("__") or file.endswith(".pyc"):
                continue                                    
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r') as f:
                    document = f.read()
                if "add_argument" not in document:
                    continue
                file_path = os.path.join(root, file)
                arguments = extract_argparse_arguments(file_path)
                if len(arguments) <= 0:
                    continue
                
                for argument in arguments:
                    if 'default' not in argument:
                        argument["default"] =  "no default value"
                    # default = input(f"Enter value for {argument[f'name']}[{argument['default']}]: ") or argument['default']
                    default = argument['default']
                    if isinstance(default, str):
                        argument["default"] = default.strip()
                    if "type" not in argument:
                        argument["type"] = "str"
                    if "help" not in argument:
                        argument["help"] = f"Commandline argument for {argument['name']}"
                    if "name" in argument:
                        name = argument["name"].strip(' ').lower().replace('.', '_')
                    else:
                        argument = json.loads(json.dumps(argument).replace("\n", "").replace("\t", "    "))
                        name = argument["default"]
                        default = f"{{os.getenv(\'{argument['default']}\')}}"
                        field_type = argument["type"]
                        help = argument["help"].strip("\n                       ")
                        argument["name"] = name
                        argument["default"] = default.strip()
                        argument["type"] = field_type
                        argument["help"] = help
                    all_arguments[name] = argument
                    if not default == None and "os.getenv" in default:
                        lines.append(f"f\"{name}={default}\"")
                    else:
                        lines.append(f"\"{name}={argument['default']}\"")
                        
                        
                        
    lines = list(set(lines))
    return all_arguments, lines
    
    
def save_file(file_path: Path, content: str):
    with open(file_path, 'w') as f:
        f.write(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python config_extractor.py <path_to_config_file>")
        sys.exit(1)

    file_dir = sys.argv[1]
    filename = str(file_dir).split('/')[-1]
    print(filename)
    paths_dict = {
        "environment_path": Path(f".{filename}.env"),
        "subnet_env_path": Path(f"module_validator/config/{filename}/.{filename}.env"),
        "configuration_path": Path(f"module_validator/config/{filename}/{filename}.yaml"),
        "pydantic_path": Path(f"module_validator/config/{filename}/{filename}_configuration.py"),
        "template_path": Path(f"module_validator/config/configuration_template.py"),
        "generated_path": Path(f"module_validator/config/{filename}/{filename}_configuration.py"),
    }
    path_lines = ''.join([f"{path}\n" for path in paths_dict.values()])
    with open(paths_dict["template_path"], "r", encoding="utf-8") as f:
        configuration_template = f.read().replace('        """', '').replace('        """', '"""').replace('"""', '')
        

    for path in paths_dict.values():
        path.parent.mkdir(parents=True, exist_ok=True)
            
    all_arguments, lines = parse_subnet_folder(file_dir)
        
    models, nested_structure = create_nested_models(all_arguments)
    save_file(paths_dict["configuration_path"], yaml.safe_dump(nested_structure, indent=2))
    
    pydantic_template, subclass_template, attribute_template, unspecified_types = generate_pydantic_model_script(models, str(paths_dict["configuration_path"]))
    save_file(paths_dict["pydantic_path"], pydantic_template)
    

    commandline_arguments = create_argument_string(all_arguments)
    configuration_template = configuration_template.replace("{{{argument_generation}}}", commandline_arguments)
    configuration_template = configuration_template.replace("{{{sub_class_generation}}}", subclass_template)
    configuration_template = configuration_template.replace("{{{attribute_generation}}}", attribute_template)
    env_lines = "\n".join(f"""            {env.strip()},""" for env in lines)
    configuration_template = configuration_template.replace("{{{environment_generation}}}", env_lines)
    save_file(paths_dict["generated_path"], configuration_template)
    
    print(f"Pydantic model with argument prompting has been written to: {path_lines}")
    
    unspecified_lines = ''.join([f"{unspecified_type.lower().strip(' ').replace('.', '_')}\n" for unspecified_type in unspecified_types])    
    print(f"""The following class attributes did not have enough information to configure with proper types for these attributes:
{unspecified_lines}
the class configuration is in {paths_dict['generated_path']}
Correction is recommended but no required.
""")
    
def custom_edge_cases(default_value: Any):
    return default_value
if __name__ == "__main__":
    
    main()