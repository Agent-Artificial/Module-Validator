import os
import re
from module_validator.custom_modules import install_registrar_module
from module_validator.config import Config
from module_validator.database import Database


def update_setup_py(module_name, module_path):
    with open("setup.py", "r") as file:
        content = file.read()

    # Find the module_validator.inference entry
    pattern = r'("module_validator\.inference"\s*:\s*\[?)(.*?)(\]?,?\s*\n)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        current_entries = match.group(2).strip()
        new_entry = f'"{module_name} = {module_path}"'

        if current_entries:
            if current_entries.endswith(","):
                updated_entries = f"{current_entries}\n        {new_entry},"
            else:
                updated_entries = f"{current_entries},\n        {new_entry}"
        else:
            updated_entries = new_entry

        updated_content = (
            content[: match.start()]
            + f"{match.group(1)}\n        {updated_entries}\n    {match.group(3)}"
            + content[match.end() :]
        )

        with open("setup.py", "w") as file:
            file.write(updated_content)
        return True
    else:
        print("Couldn't find the module_validator.inference entry in setup.py")
        return False


def add_command(db):
    name = input("Enter command name: ").strip()
    module_name = input("Enter module name: ").strip()
    description = input("Enter command description (optional): ").strip()

    db.add_command(name, module_name, description)
    print(f"Command '{name}' added successfully.")


def list_commands(db):
    commands = db.list_commands()
    if commands:
        print("Available commands:")
        for command in commands:
            print(f"- {command.name} (Module: {command.module_name})")
    else:
        print("No commands found.")


def delete_command(db):
    name = input("Enter command name to delete: ").strip()
    db.delete_command(name)
    print(f"Command '{name}' deleted.")


def register_module():
    module_name = input("Enter the name of the module to register: ").strip()
    if not module_name:
        print("Module name cannot be empty.")
        return

    custom_module = input("Is this a custom module? (y/n): ").strip().lower() == "y"
    print(custom_module)
    if custom_module:
        install_registrar_module(module_name)
    module_dir = os.path.join("module_validator", "modules", module_name)
    module_file = os.path.join(module_dir, f"{module_name}.py")

    if not os.path.exists(module_file):
        os.makedirs(module_dir, exist_ok=True)
        print(f"Find the module file  {module_file}")

    module_path = f"module_validator.modules.{module_name}.{module_name}:process"

    # Update setup.py
    if update_setup_py(module_name, module_path):
        print(f"Updated setup.py with new module: {module_name}")
    else:
        print("Failed to update setup.py")
        return


def run_module():

    print("Select a module to run:")


def main():
    config = Config()
    config.load_configs()
    db = Database(config.get_global_config())

    while True:
        print("\nCommand Management CLI")
        print("1. Add command")
        print("2. List commands")
        print("3. Delete command")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            add_command(db)
        elif choice == "2":
            list_commands(db)
        elif choice == "3":
            delete_command(db)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
