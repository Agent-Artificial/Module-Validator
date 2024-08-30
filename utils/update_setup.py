import ast
import re
from typing import Dict, Any

def add_module_to_setup(module_name: str) -> None:
    """
    Adds a module entry to the setup.py file under the entry_points section.

    Args:
        module_name (str): The name of the module to add to the entry_points.

    Returns:
        None
    """
    # Read the current setup.py file
    with open("setup.py", "r") as file:
        setup_content = file.read()

    # Use regex to find the entry_points dictionary
    entry_points_match = re.search(r"entry_points\s*=\s*({.*?})", setup_content, re.DOTALL)
    if not entry_points_match:
        print("entry_points not found in setup.py")
        return

    entry_points_str = entry_points_match.group(1)
    entry_points: Dict[str, Any] = ast.literal_eval(entry_points_str)

    # Modify the entry_points dictionary
    key = "module_validator.inference"
    new_entry = f"{module_name} = module_validator.modules.{module_name}.{module_name}:process"
    if key in entry_points:
        if isinstance(entry_points[key], list):
            entry_points[key].append(new_entry)
        else:
            entry_points[key] = [entry_points[key], new_entry]
    else:
        entry_points[key] = [new_entry]

    # Convert the modified entry_points back to a string
    modified_entry_points_str = repr(entry_points)

    # Replace the old entry_points with the modified one in the setup_content
    modified_content = setup_content.replace(entry_points_str, modified_entry_points_str)

    # Write the modified content back to setup.py
    with open("setup.py", "w") as file:
        file.write(modified_content)

    print(f"Added {module_name} to setup.py successfully.")


