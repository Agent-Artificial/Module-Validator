import importlib.metadata
import os
import importlib
from .database import Database
from module_validator.configurator import Config
import pkg_resources
import sys


class ModuleRegistry:
    def __init__(self, config: Config, db: Database = None):
        self.config = config
        self.db = db or Database(config.get_global_config())
        self.modules = {}

    def load_modules(self):
        print("Starting to load modules...")
        entry_points = list(
            pkg_resources.iter_entry_points(group="module_validator.inference")
        )
        print(f"Found {len(entry_points)} entry points")

        for entry_point in entry_points:
            print(
                f"Attempting to load: {entry_point.name} = {entry_point.module_name}:{entry_point.attrs[0]}"
            )
            try:
                module = importlib.import_module(entry_point.module_name)
                print(f"Successfully imported module: {entry_point.module_name}")

                module_function = getattr(module, entry_point.attrs[0])
                print(f"Successfully got attribute: {entry_point.attrs[0]}")

                self.modules[entry_point.name] = module_function
                print(f"Successfully registered module: {entry_point.name}")
            except Exception as e:
                print(f"Failed to load module {entry_point.name}: {e}")
                print(f"Exception type: {type(e).__name__}")
                print(f"Module search path: {sys.path}")

    def get_module(self, name):
        return self.modules.get(name)

    def list_modules(self):
        return list(self.modules.keys())

    def _load_module(self, name, entry_point):
        try:
            module = importlib.import_module(entry_point)
            return getattr(module, name)
        except (ImportError, AttributeError):
            print(f"Failed to load module: {name}")
            return None

    def register_module(self, name, version, entry_point, config=None):
        module = self._load_module(name, entry_point)
        if module:
            self.modules[name] = module
            self.db.add_module(name, version, entry_point, config)
            if hasattr(module, "configure"):
                module.configure(config or {})
            return True
        return False

    def unregister_module(self, name):
        if name in self.modules:
            del self.modules[name]
            self.db.delete_module(name)
            return True
        return False

    def _load_module(self, name, entry_point):
        try:
            module = importlib.import_module(entry_point)
            return getattr(
                module, name.capitalize()
            )  # Return the class, not an instance
        except (ImportError, AttributeError) as e:
            print(f"Failed to load module: {name}. Error: {e}")
            return None


def main():
    registry = ModuleRegistry()
    registry.load_modules()

    print("Available modules:", registry.list_modules())

    # Example usage
    embedding_module = registry.get_module("embedding")
    if embedding_module:
        result = embedding_module("sample text")
        print("Embedding result:", result)


if __name__ == "__main__":
    main()
