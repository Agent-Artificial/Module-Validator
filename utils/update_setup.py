import ast
import astor


def add_module_to_setup(module_name):
    # Read the current setup.py file
    with open("setup.py", "r") as file:
        setup_content = file.read()

    # Parse the content into an AST
    tree = ast.parse(setup_content)

    # Find the setup function call
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "setup"
        ):
            # Find the entry_points argument
            for keyword in node.keywords:
                if keyword.arg == "entry_points":
                    # Find the module_validator.inference key in the dictionary
                    for key in keyword.value.keys:
                        if (
                            isinstance(key, ast.Str)
                            and key.s == "module_validator.inference"
                        ):
                            new_entry = f"{module_name} = module_validator.modules.{module_name}.{module_name}:process"
                            if isinstance(key.value, ast.List):
                                key.value.elts.append(ast.Str(s=new_entry))
                            elif isinstance(key.value, ast.Tuple):
                                new_elts = key.value.elts + [ast.Str(s=new_entry)]
                                key.value = ast.Tuple(elts=new_elts, ctx=ast.Load())
                            elif isinstance(key.value, ast.Str):
                                # If it's a string, convert it to a list with the existing entry and the new one
                                existing_entry = key.value.s
                                key.value = ast.List(
                                    elts=[
                                        ast.Str(s=existing_entry),
                                        ast.Str(s=new_entry),
                                    ],
                                    ctx=ast.Load(),
                                )
                            else:
                                print(
                                    f"Unexpected type for module_validator.inference value: {type(key.value)}"
                                )
                                return

    # Convert the modified AST back to source code
    modified_content = astor.to_source(tree)

    # Write the modified content back to setup.py
    with open("setup.py", "w") as file:
        file.write(modified_content)

    print(f"Added {module_name} to setup.py successfully.")


if __name__ == "__main__":
    module_name = input("Enter the name of the new module: ")
    add_module_to_setup(module_name)
