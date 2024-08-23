import yaml
import json
from pydantic import create_model, Field
from typing import Any, Dict, List, Union


def yaml_to_pydantic(yaml_file_path: str) -> Any:
    with open(yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
    return dict_to_pydantic(yaml_data)

def dict_to_pydantic(data: Dict[str, Any], model_name: str = "YamlModel") -> Any:
    fields = {}
    for key, value in data.items():
        if isinstance(value, dict):
            fields[key] = (dict_to_pydantic(value, f"{key.capitalize()}Model"), ...)
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                fields[key] = (List[dict_to_pydantic(value[0], f"{key.capitalize()}ItemModel")], ...)
            else:
                fields[key] = (List[type(value[0]) if value else Any], ...)
        else:
            fields[key] = (type(value), Field(default=value))
    
    return create_model(model_name, **fields)



def model_to_python_code(model: Any, model_name: str) -> str:
    imports = [
        "from pydantic import BaseModel, Field",
        "from typing import List, Optional, Any, Union",
        "",
        ""
    ]
    
    def _model_to_code(m, name):
        lines = [f"class {name}(BaseModel):"]
        for field_name, field in m.__fields__.items():
            if hasattr(field, "outer_type_"):
                field_type = field.outer_type_
                if getattr(field_type, "__origin__", None) is Union:
                    field_type = f"Optional[{field_type.__args__[0].__name__}]"
                elif getattr(field_type, "__origin__", None) is list:
                    if hasattr(field_type.__args__[0], "__name__"):
                        field_type = f"List[{field_type.__args__[0].__name__}]"
                    else:
                        field_type = "List[Any]"
                else:
                    field_type = field_type.__name__

                default = f" = {repr(field.default)}" if not isinstance(field.default, type(...)) else ""
                lines.append(f"    {field_name}: {field_type}{default}")
            lines.append("")  # Add an empty line after each class definition
            return "\n".join(lines)
    
    code = ""
    models = [model]
    processed = set()
    
    while models:
        m = models.pop(0)
        if m.__name__ in processed:
            continue
        processed.add(m.__name__)
        code += _model_to_code(m, m.__name__)
        for field in m.__fields__.values():
            if hasattr(field, "type_"):
                if hasattr(field.type_, "__fields__"):
                    models.append(field.type_)
                elif getattr(field.type_, "__origin__", None) is list:
                    if hasattr(field.type_.__args__[0], "__fields__"):
                        models.append(field.type_.__args__[0])
    
    return "\n".join(imports) + code

if __name__ == "__main__":
    yaml_file_path = "module_validator/config/generated_config.yaml"
    try:
        model = yaml_to_pydantic(yaml_file_path)
        
        with open("generated_pydantic_model.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(model), indent=4)
        python_code = model_to_python_code(model, model.__name__)          
        
        # Save the code to a .py file
        output_file = "generated_pydantic_model.py"
        with open(output_file, "w") as file:
            file.write(python_code)
        
        print(f"Pydantic model has been created and saved to '{output_file}'")
        print("Here's a preview of the generated code:")
        print(python_code[:500] + "..." if len(python_code) > 500 else python_code)
        
    except ValueError as e:
        raise ValueError("Generated code is not valid Python syntax")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Here's the generated code for debugging:")
        print(python_code)