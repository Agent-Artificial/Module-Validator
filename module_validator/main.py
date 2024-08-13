import sys
import argparse
import importlib
from typing import Callable
import pkg_resources
from module_validator.modules.module import Module
from module_validator.config import Config
from module_validator.registry import ModuleRegistry

def default_output(output:str) -> None:
    print("This is the default output", output)
    
def debug_entry_points():
    print("Debugging entry points:")
    for group in ['console_scripts', 'module_validator.module', 'module_validator.inference']:
        print(f"\nGroup: {group}")
        for ep in pkg_resources.iter_entry_points(group=group):
            print(f"  {ep.name} = {ep.module_name}:{ep.attrs[0]}")

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
    print("Starting main function")
    debug_entry_points()

    try:
        config = Config()
        config.load_configs()
        registry = ModuleRegistry(config)
        registry.load_modules()
        
        print("Loaded modules:", registry.list_modules())
        
        # Test the embedding module
        embedding_process = registry.get_module('embedding')
        if embedding_process:
            test_text = "Hello, this is a test for the embedding module!"
            embedding_config = config.get_config('embedding').get('embedding', {})
            result = embedding_process(test_text, embedding_config)
            print(f"Embedding result (first 5 dimensions): {result[:5]}")
        else:
            print("Embedding module not found. Make sure it's properly registered.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Traceback:")
        traceback.print_exc()

    return 0

if __name__ == "__main__":
    sys.exit(main())