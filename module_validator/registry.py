import importlib.metadata
import os

class ModuleRegistry:
    def __init__(self):
        self.modules = {}

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

    def get_module(self, name):
        return self.modules.get(name)

    def list_modules(self):
        return list(self.modules.keys())

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