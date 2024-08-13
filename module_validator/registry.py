import importlib.metadata
import os
import importlib
from .database import Database
from .config import Config


class ModuleRegistry:
    def __init__(self, config: Config):
        self.config = config
        self.db = Database(config.get_global_config())
        self.modules = {}

    def load_modules(self):
        self.db.create_tables()  # Ensure tables exist
        db_modules = self.db.list_modules()
        
        for db_module in db_modules:
            module = self._load_module(db_module.name, db_module.entry_point)
            if module:
                self.modules[db_module.name] = module
                if hasattr(module, 'configure'):
                    module.configure(db_module.config or {})

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
            if hasattr(module, 'configure'):
                module.configure(config or {})
            return True
        return False

    def unregister_module(self, name):
        if name in self.modules:
            del self.modules[name]
            self.db.delete_module(name)
            return True
        return False

    def get_module(self, name):
        return self.modules.get(name)

    def list_modules(self):
        return list(self.modules.keys())

    def load_modules(self):
        # Load modules from entry points
        for ep in importlib.metadata.entry_points().select(group='module_validator.inference'):
            self.modules[ep.name] = ep.load()

        # Load modules from a specific directory
        module_dir = os.path.join(os.path.dirname(__file__), 'custom_modules')
        if os.path.exists(module_dir):
            for filename in os.listdir(module_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    module_name = filename[:-3]
                    module = importlib.import_module(f'module_validator.custom_modules.{module_name}')
                    if hasattr(module, 'inference'):
                        self.modules[module_name] = module.inference

def main():
    registry = ModuleRegistry()
    registry.load_modules()

    print("Available modules:", registry.list_modules())

    # Example usage
    embedding_module = registry.get_module('embedding')
    if embedding_module:
        result = embedding_module("sample text")
        print("Embedding result:", result)

if __name__ == "__main__":
    main()