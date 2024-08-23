import os
import re
import ast
import sys
import json
import yaml
import bittensor as bt
from typing import Dict, Any, List, ClassVar
from pydantic import create_model, Field, BaseModel
from pathlib import Path


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
            arg_info['name'] = arg.s.lstrip('-')
            name = arg.s.replace('.', "_").replace("-", "_")
    for keyword in node.keywords:
        if keyword.arg == 'type':
            if isinstance(keyword.value, ast.Name):
                arg_info['type'] = keyword.value.id
            elif isinstance(keyword.value, ast.Attribute):
                arg_info['type'] = f"""{keyword.value.value.id}.{keyword.value.attr}"""
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
    if isinstance(node, (ast.Constant, ast.Constant, ast.Constant)):
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
        else:
            if parts[0] not in nested_structure:
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


def generate_pydantic_model_script(models, output_file: str):
    full_code = """from pydantic import BaseModel, Field\nfrom typing import Any\n\n
from dotenv import load_dotenv
import os

load_dotenv()

"""
    # Generate class definitions for nested structures
    classnames = []
    atributes = []
    field_type = None
    defaults = {}
    class_template = ""
    config_template = "class Config(BaseModel):\n"
    config_template += "".join([f"    {classname.lower()}: {classname}Config = Field(default_factory={classname}Config())\n" for classname in classnames if classname.isupper()])
    
    for class_name, model in models.items():
        if model.__fields__:
            class_template += f"class {class_name}Config(BaseModel):\n"
            classnames.append(class_name)
            for name, field in model.__fields__.items():
                atributes.append(name)
                field_type = field.annotation.__name__
                default = field.default if not isinstance(field.default, type(...)) else None
                if field_type == 'str':
                    default = f'"{default}"'.strip("'")
                defaults[name] = default
                description = field.field_info.description if hasattr(field, 'field_info') else None
                if description:
                    class_template += f"    {name}: {field_type} = Field(default={default!r}, description={description!r})\n"
                else:
                    class_template += f"    {name}: {field_type} = {default!r}\n"
            class_template += "\n\n"
            if len(model.__fields__) > 1:
                # Nested structure
                config_template += f"    {name.lower()}: {field_type} = Field(default={defaults[name] if name in defaults else name.title() + 'Config'})\n"
            else:
                # Single field model
                field_name, field = next(iter(model.__fields__.items()))
                field_type = field.annotation.__name__
                description = field.field_info.description if hasattr(field, 'field_info') else None                
                if description:
                    config_template += f"    {name.lower()}: {field_type} = Field(default={defaults[field_name]!r}, description={description!r})\n"
                else:
                    config_template += f"    {name.lower()}: {field_type} = {defaults[field_name]!r}\n"
                    
        else:
            if isinstance(model, object):
                config_template += f'    {class_name}: Any = Field(default=None)\n'
                
    for name in classnames:
        config_template += f"    {name.lower()}: {name}Config = Field(default_factory={name}Config())\n"        
        
            
    full_code = full_code + class_template + config_template

    # Add get method to Config class
    full_code += "\n    def get(self, key: str, default: Any = None) -> Any:\n"
    full_code += "        parts = key.split('.')\n"
    full_code += "        value = self\n"
    full_code += "        for part in parts:\n"
    full_code += "            if isinstance(value, BaseModel):\n"
    full_code += "                value = getattr(value, part, default)\n"
    full_code += "            elif isinstance(value, dict):\n"
    full_code += "                value = value.get(part, default)\n"
    full_code += "            else:\n"
    full_code += "                return default\n"
    full_code += "            if value is None:\n"
    full_code += "                return default\n"
    full_code += "        return value\n"

    with open(output_file, 'w') as f:
        f.write(full_code)
    return full_code
    
def main():
    if len(sys.argv) < 2:
        print("Usage: python config_extractor.py <path_to_config_file>")
        sys.exit(1)

    file_dir = sys.argv[1]
    filename = str(file_dir).split('/')[-1]
    environment_path = Path(f".{filename}.env")
    configuration_path = Path(f"module_validator/{filename}/{filename}.yaml")
    configurator_path = Path(f"module_validator/{filename}/{filename}_configuration.py")
    if not os.path.exists(configuration_path):
        configuration_path.parent.mkdir(parents=True, exist_ok=True)
    
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
                    argument["default"] = default
                    if "type" not in argument:
                        argument["type"] = "str"
                    if "help" not in argument:
                        argument["help"] = f"Commandline argument for {argument['name']}"
                    if "name" in argument:
                        name = argument["name"]
                        all_arguments[name] = argument
                        lines.append(f"{name}={argument['default']}")
                
    with open("all_arguments.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(all_arguments, indent=4))
        
    models, nested_structure = create_nested_models(all_arguments)

    with open(configuration_path, "w", encoding="utf-8") as f:
        f.write(yaml.safe_dump(nested_structure, indent=4))
        
    fullcode = generate_pydantic_model_script(models, str(configuration_path))
         
    with open(configurator_path, "w", encoding="utf-8") as f:
        f.write(fullcode)
        
    with open(environment_path, "w", encoding="utf-8") as f:
        f.write("\n".join(f"{env}" for env in lines))

    print(f"Pydantic model with argument prompting has been written to {configuration_path}\n{configurator_path}\n{environment_path} has been created.")

if __name__ == "__main__":
    
    main()