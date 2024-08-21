import os
import re
import ast
import sys
import json
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
    

def create_nested_models(arguments: List[Dict[str, Any]]):
    nested_structure = {}
    for arg in arguments:
        print(arg)
        parts = None
        if "name" in arg:
            parts = arg['name'].split('.')
        else:
            continue
        if len(parts) == 1:
            nested_structure[parts[0]] = arg
        else:
            if parts[0] not in nested_structure:
                nested_structure[parts[0]] = {}
            nested_structure[parts[0]][parts[1]] = arg

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

    return models


def generate_pydantic_model_script(models, output_file: str):
    full_code = """from pydantic import BaseModel, Field\nfrom typing import Any\n\n
from dotenv import load_dotenv
import os

load_dotenv()
    """
    # Generate class definitions for nested structures
    environment = []
    classnames = list(models.keys())
    for class_name, model in models.items():
        if model.__fields__:
            full_code += f"class {class_name}Config(BaseModel):\n"
            for name, field in model.__fields__.items():
                field_type = field.annotation.__name__
                default = input(f"Enter value for {name}[{field.default}]: " or field.default)
                environment.append(f"{name}={field.default}")
                description = field.field_info.description if hasattr(field, 'field_info') else None
                if description:
                    full_code += f"    {name}: {field_type} = Field(default={default!r}, description={description!r})\n"
                else:
                    full_code += f"    {name}: {field_type} = {default!r}\n"
            full_code += "\n"

    # Generate main Config class
    full_code += "class Config(BaseModel):\n"
    full_code += "".join([f"    {classname.lower()}: Any = {classname}Config()\n" for classname in classnames])
    for name, model in models.items():
        if model.__fields__:
            if len(model.__fields__) > 1:
                # Nested structure
                full_code += f"    {name.lower()}: {name} = Field(default={default})\n"

            else:
                # Single field model
                field_name, field = next(iter(model.__fields__.items()))
                field_type = field.annotation.__name__
                default = input(f"Enter value for {name}[{default}]: ") or field.default
                description = field.field_info.description if hasattr(field, 'field_info') else None
                
                if description:
                    full_code += f"    {name.lower()}: {field_type} = Field(default={model.default!r}, description={description!r})\n"
                else:
                    full_code += f"    {name.lower()}: {field_type} = {field.default!r}\n"
        else:
            # Empty model, add as Any type with None default
            full_code += f"    {name.lower()}: {field_type} = {field.default}\n"
    
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
        return full_code, environment
    
def main():
    if len(sys.argv) < 2:
        print("Usage: python config_extractor.py <path_to_config_file>")
        sys.exit(1)

    file_dir = sys.argv[1]
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
                        argument["default"] = f"no default value"
                    if "type" not in argument:
                        argument["type"] = "str"
                    if "help" not in argument:
                        argument["help"] = f"Commandline argument for {argument['name']}"
                    if "name" in argument:
                        all_arguments[argument["name"]] = argument
                        
                nodes: ast.Call = ast.parse(open(file_path).read()).body[0]
                for node in ast.walk(nodes):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument':
                        if node:
                            all_arguments[node['name']] = node
                
    modules = {}                
    for name, argument in all_arguments.items():
        parent = None
        if "." in name:
            parent = name.split(".")[0]
            child = name.split(".")[1]
            modules[parent] = {child: argument["default"]}
        else:
            parent = name
            modules[parent] = argument["default"]
    with open("generated_config.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(modules, indent=4))
        
    output_file = "config_model.py"
    
    models = create_nested_models([argument for argument in all_arguments.values()])
    
    full_code, environment = generate_pydantic_model_script(models, output_file)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_code)
        
    env_file = f".{output_file.split('.')[0]}.env"
    
    with open(env_file, "w", encoding="utf-8") as f:
        f.write("\n".join(f"{env}" for env in environment))

    print(f"Pydantic model with argument prompting has been written to {output_file}")

if __name__ == "__main__":
    
    main()