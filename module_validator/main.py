import sys
import argparse
import importlib.metadata
from typing import Callable
from module_validator.modules.module import Module
from module_validator.config import Config
from module_validator.registry import ModuleRegistry

def default_output(output:str) -> None:
    print("This is the default output", output)


def create_module(outputer_type: str, outputer: str):
    eps = importlib.metadata.entry_points().select(group='module-validator.module')
    outputers = {
        entrypoint.name: entrypoint
        for entrypoint in eps
    }
    try:
        outputer = outputers[outputer].load()
    except KeyError:
        print(f"outputer {outputer} is not available", file=sys.stderr)
        outputers_s = ", ".join(sorted(outputers))
        print(f"available outputers: {outputers_s}", file=sys.stderr)
        return 1
    return outputer(outputer_type)
        
create_module_functions: dict[str, Callable[..., Module]] = {}

def register(module_type: str, create_function: Callable[..., Module]):
    outputer = create_module(module_type, create_function)
    create_module_functions[module_type] = outputer
    
    
def unregister(module_type:str):
    create_module_functions.pop(module_type, None)

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("module_type", type=str, choices=create_module_functions.keys())
    parser.add_argument("output", type=str)
    return parser.parse_args()



def main():
    config = Config()
    config.load_configs()
    registry = ModuleRegistry(config)
    return registry.load_moduels()
    
    
def example(config):
    registry = ModuleRegistry(config)
    # Register a new module
    registry.register_module('new_module', '1.0', 'path.to.new_module', {'some_config': 'value'})

    # Use a module
    module = registry.get_module('embedding')
    if module:
        result = module("sample text")
        print(result)


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    exit(register("default", default_output))