import asyncio
import sys
import argparse
import importlib
import traceback
from typing import Callable
import pkg_resources
from module_validator.config import Config
from module_validator.module import Module
from module_validator.registry import ModuleRegistry
from module_validator.database import Database

def default_output(output:str) -> None:
    print("This is the default output", output)
    
    
async def execute_command(registry, db, command_name, data, params):
    command = db.get_command(command_name)
    if not command:
        print(f"Command '{command_name}' not found.")
        return

    module = registry.get_module(command.module_name)
    if not module:
        print(f"Module '{command.module_name}' not found.")
        return

    data = {
        "data": {
            "input": data,
            **params
            }
        }
    
    result = await module(data)
    print(f"Command '{command_name}' executed. Result: {result}")
    
    
def debug_entry_points():
    print("Debugging entry points:")
    for group in ['console_scripts', 'module_validator.module', 'module_validator.inference', 'module_validator.command']:
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

async def main():
    print("Starting main function")
    debug_entry_points()

    try:
        config = Config()
        config.load_configs()
        db = Database(config.get_global_config())
        registry = ModuleRegistry(config, db)
        registry.load_modules()
        if len(sys.argv) < 2:
            print("Usage: python -m module_validator.main <command> [data] [params]")
            return
        else:
            command = sys.argv[1]
            data = sys.argv[2] if len(sys.argv) > 2 else ""
            params = eval(sys.argv[3]) if len(sys.argv) > 3 else {}

            await execute_command(registry, db, command, data, params)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Traceback:")
        traceback.print_exc()

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))