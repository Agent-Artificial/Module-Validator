import argparse
import os
import requests
import json
import subprocess
import importlib
from typing import Any, Dict
from module_validator.config import Config

ENV = os.getenv('MODULE_VALIDATOR_ENV', 'development')

configurator = Config("module_validator/config")

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("module_type", type=str)
    parser.add_argument("output", type=str)
    return parser.parse_args()

def install_registrar_module(module_name: str) -> bool:
    api_url = f"https://registrar-cellium.ngrok.app/modules/{module_name}"
    
    try:
        # Make API call to get the module installer
        response = requests.get(api_url)
        response.raise_for_status()
        
        installer_data = response.json()
        
        if 'file' not in installer_data:
            raise ValueError("Invalid response from API: 'file' key not found")
        
        # Save the installer file
        installer_path = f"{module_name}_installer.py"
        with open(installer_path, 'w') as f:
            f.write(installer_data['file'])
        
        # Run the installer
        subprocess.run(['python', installer_path], check=True)
        
        # Clean up the installer file
        os.remove(installer_path)
        
        # Verify the module structure
        module_path = f"modules/{module_name}/{module_name}.py"
        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Module file not found at {module_path}")
        
        # Import and validate the module
        module = importlib.import_module(f"modules.{module_name}.{module_name}")
        module_class = getattr(module, f"{module_name.capitalize()}")
        
        if not hasattr(module_class, 'process'):
            raise AttributeError(f"Module class {module_name.capitalize()} does not have a 'process' method")
        
        print(f"Successfully installed and verified module: {module_name}")
        return True
    
    except requests.RequestException as e:
        print(f"Error making API request: {e}")
    except json.JSONDecodeError:
        print("Error decoding API response")
    except subprocess.CalledProcessError:
        print("Error running the installer script")
    except ImportError:
        print(f"Error importing the installed module: {module_name}")
    except (ValueError, FileNotFoundError, AttributeError) as e:
        print(f"Error verifying module structure: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return False

def main():
    args = parseargs()
    module = args.module_type
    
    if install_registrar_module(module):
        print(f"Module {module} installed successfully")
    else:
        print(f"Failed to install module {module}")

if __name__ == "__main__":
    main()