import ast
import sys
import json
from typing import Dict, Any, List, ClassVar
from pydantic import create_model, Field, BaseModel


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
        if isinstance(arg, ast.Str) and arg.s.startswith('--'):
            arg_info['name'] = arg.s.lstrip('-')

    for keyword in node.keywords:
        if keyword.arg == 'type':
            if isinstance(keyword.value, ast.Name):
                arg_info['type'] = keyword.value.id
            elif isinstance(keyword.value, ast.Attribute):
                arg_info['type'] = f"""{keyword.value.value.id}.{keyword.value.attr}"""
        elif keyword.arg == 'default':
            arg_info['default'] = parse_default_value(keyword.value)
        elif keyword.arg == 'help':
            if isinstance(keyword.value, ast.Str):
                arg_info['help'] = keyword.value.s
        elif keyword.arg == 'action':
            if isinstance(keyword.value, ast.Str):
                arg_info['action'] = keyword.value.s

    return arg_info


def parse_default_value(node):
    if isinstance(node, (ast.Str, ast.Num, ast.NameConstant)):
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
        parts = arg['name'].split('.')
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
    full_code = "from pydantic import BaseModel, Field\nfrom typing import Any\n\n"
    
    # Generate class definitions for nested structures
    for class_name, model in models.items():
        if model.__fields__:
            full_code += f"class {class_name}(BaseModel):\n"
            for name, field in model.__fields__.items():
                field_type = field.annotation.__name__
                default = input(f"Enter value for {name}[{field.default}]: " or field.default)
                description = field.field_info.description if hasattr(field, 'field_info') else None
                
                if description:
                    full_code += f"    {name}: {field_type} = Field(default={default!r}, description={description!r})\n"
                else:
                    full_code += f"    {name}: {field_type} = {default!r}\n"
            full_code += "\n"

    # Generate main Config class
    full_code += "class Config(BaseModel):\n"
    full_code += "    wallet: Any = None\n"
    full_code += "    subtensor: Any = None\n"
    full_code += "    neuron: Any = None\n"
    full_code += "    axon: Any = None\n"
    full_code += "    metagraph: Any = None\n"
    for name, model in models.items():
        if model.__fields__:
            if len(model.__fields__) > 1:
                # Nested structure
                full_code += f"    {name.lower()}: {name} = Field(default_factory={name})\n"

            else:
                # Single field model
                field_name, field = next(iter(model.__fields__.items()))
                field_type = field.annotation.__name__
                default = input(f"Enter value for {name}[{field.default}]: " or field.default)
                description = field.field_info.description if hasattr(field, 'field_info') else None
                
                if description:
                    full_code += f"    {name.lower()}: {field_type} = Field(default={default!r}, description={description!r})\n"
                else:
                    full_code += f"    {name.lower()}: {field_type} = {default!r}\n"
        else:
            # Empty model, add as Any type with None default
            full_code += f"    {name.lower()}: Any = None\n"
    
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

    # Add prompt_for_values function
    full_code += "\ndef prompt_for_values(config: Config):\n"
    full_code += "    for field_name, field in config.__fields__.items():\n"
    full_code += "        if isinstance(field.type_, type) and issubclass(field.type_, BaseModel):\n"
    full_code += "            nested_config = getattr(config, field_name)\n"
    full_code += "            print(f'Configuring {field_name}:')\n"
    full_code += "            prompt_for_values(nested_config)\n"
    full_code += "        else:\n"
    full_code += "            default = getattr(config, field_name)\n"
    full_code += "            description = field.field_info.description\n"
    full_code += "            default_str = f' (default: {default})' if default is not None else ''\n"
    full_code += "            prompt = f'Enter value for {field_name}{default_str}'\n"
    full_code += "            if description:\n"
    full_code += "                prompt += f' ({description})'\n"
    full_code += "            prompt += ', or press Enter to keep default: '\n"
    full_code += "            value = input(prompt)\n"
    full_code += "            if value:\n"
    full_code += "                try:\n"
    full_code += "                    if field.type_ == bool:\n"
    full_code += "                        typed_value = value.lower() in ('true', 'yes', '1', 'on')\n"
    full_code += "                    elif field.type_ == int:\n"
    full_code += "                        typed_value = int(value)\n"
    full_code += "                    elif field.type_ == float:\n"
    full_code += "                        typed_value = float(value)\n"
    full_code += "                    else:\n"
    full_code += "                        typed_value = value\n"
    full_code += "                    setattr(config, field_name, typed_value)\n"
    full_code += "                except ValueError:\n"
    full_code += "                    print(f'Invalid input for {field_name}. Using default value.')\n"

    with open(output_file, 'w') as f:
        f.write(full_code)

def main():
    if len(sys.argv) < 2:
        print("Usage: python config_extractor.py <path_to_config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    arguments = extract_argparse_arguments(config_file)
    models = create_nested_models(arguments)
    
    output_file = "config_model.py"
    generate_pydantic_model_script(models, output_file)
    
    print(f"Pydantic model with argument prompting has been written to {output_file}")

if __name__ == "__main__":
    main()