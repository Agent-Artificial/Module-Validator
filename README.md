# Module Validator

Module Validator is a flexible Python package for dynamically loading and using inference modules, starting with an embedding function. It provides a simple interface for managing and utilizing various inference modules in your projects.

The validator is composed of three primary components.

1. **Subnet Module**: Defines the validator and miner configuration and objects for interacting with the chain. 
2. **Inference Module**: Contains the code required to run specific kinds of inference for use in the Subnet Modulle. 
3. **Module Validator**: Handles instillation, configuration, as well as running the Subnet code in a properly configured environment.


## Inference Modules

### Installation

You can install Module Validator using pip:

```bash
pip install module_validator
```

### Usage
#### Configuration

Module Validator uses a flexible configuration system that supports different environments and module-specific settings, organized in a nested structure.

#### Directory Structure

Create a `config` directory in your project with the following structure:

```
module_validator/
    config/
        development/
            global.yaml
            embedding.yaml
            other_module.yaml
        production/
            global.yaml
            embedding.yaml
            other_module.yaml
        staging/
            global.yaml
            embedding.yaml
            other_module.yaml
```

#### Configuration Files

1. Global configuration: `{environment}/global.yaml`
   Contains settings that apply to all modules in a specific environment.

2. Module-specific configuration: `{environment}/{module_name}.yaml`
   Contains settings specific to a particular module in a specific environment.

#### Environment Selection

Set the `MODULE_VALIDATOR_ENV` environment variable to choose the configuration environment. If not set, it defaults to 'development'.

```bash
export MODULE_VALIDATOR_ENV=production
```

##### Using Configurations in Modules

When creating a custom module, you can access its configuration by implementing a `configure` method:

```python
def inference(input_text):
    # Your inference logic here
    return result

def configure(config):
    # Set up your module using the provided configuration
    global_setting = config.get('global_setting')
    module_specific_setting = config.get('module_specific_setting')
```

The `configure` method will be called automatically when the module is loaded, providing it with the merged global and module-specific configuration for the current environment.

#### Adding New Environments

To add a new environment:

1. Create a new directory under `config/` with the environment name (e.g., `config/staging/`).
2. Add a `global.yaml` file in this new directory with the global settings for this environment.
3. Add module-specific YAML files as needed (e.g., `embedding.yaml`).

The configuration system will automatically detect and use the new environment when `MODULE_VALIDATOR_ENV` is set to the new environment name.

#### Basic Usage

Here's a simple example of how to use Module Validator:

```python
from module_validator import ModuleRegistry

# Initialize the registry and load modules
registry = ModuleRegistry()
registry.load_modules()

# List available modules
print("Available modules:", registry.list_modules())

# Use the embedding module
embedding_module = registry.get_module('embedding')
if embedding_module:
    result = embedding_module("sample text")
    print("Embedding result:", result)
```

#### Command Line Interface

Module Validator also provides a command-line interface:

```bash
module_validator list  # List all available modules
module_validator run embedding "sample text"  # Run the embedding module with input
```

### Extending Inference Modules

You can extend Module Validator by adding your own inference modules. There are two ways to do this:

#### 1. Creating a PyPI Package

1. Create a new Python package for your module.
2. In your package's `setup.py`, add an entry point under the `module_validator.inference` group:

   ```python
   setup(
       # ...
       entry_points={
           'module_validator.inference': [
               'my_module = my_package.module:inference_function',
           ],
       },
   )
   ```

3. Install your package using pip.

#### 2. Adding a Custom Module File

1. Create a Python file in the `custom_modules` directory of your project.
2. In this file, define a function named `inference`:

   ```python
   # my_custom_module.py
   def inference(input_text):
       # Your inference logic here
       return result
   ```

3. Module Validator will automatically detect and load this module.


### Database Integration

Module Validator now uses a database to store module registrar data, providing persistence and improved management of modules.

#### Database Configuration

In your global configuration file (`config/{environment}/global.yaml`), add the following:

```yaml
database_url: 'sqlite:///module_validator.db'
```

You can replace the SQLite URL with any other database URL supported by SQLAlchemy (e.g., PostgreSQL, MySQL).

#### Module Storage

Modules are now stored in the database with the following information:
- Name
- Version
- Entry point
- Configuration (as JSON)
- Creation and update timestamps

#### Using the Database-Backed Module Registry

The `ModuleRegistry` class now interacts with the database to load, register, and unregister modules.

```python
from module_validator.config import Config
from module_validator.registry import ModuleRegistry

config = Config()
config.load_configs()
registry = ModuleRegistry(config)

# Load modules from the database
registry.load_modules()

# Register a new module
registry.register_module('new_module', '1.0', 'path.to.new_module', {'some_config': 'value'})

# Use a module
module = registry.get_module('embedding')
if module:
    result = module("sample text")
    print(result)

# Unregister a module
registry.unregister_module('old_module')
```

#### Benefits of Database Integration

1. Persistence: Module information is stored between application restarts.
2. Versioning: Keep track of module versions.
3. Dynamic updates: Register or unregister modules at runtime.
4. Centralized configuration: Store module-specific configurations in the database.

#### Database Operations

The `Database` class provides methods for CRUD operations on modules:
- `add_module`: Add a new module to the database.
- `get_module`: Retrieve a module's information.
- `update_module`: Update an existing module's information.
- `delete_module`: Remove a module from the database.
- `list_modules`: Get all registered modules.

These operations are abstracted away by the `ModuleRegistry` class, but you can access them directly if needed for advanced use cases.

### API Reference

#### ModuleRegistry

The main class for managing inference modules.

##### Methods:

- `load_modules()`: Load all available modules from entry points and custom modules directory.
- `get_module(name)`: Get a specific module by name.
- `list_modules()`: List all available modules.

#### LLM Instructions:

You can use these instructions to have an advanced LLM like Claude 3.5 for ChatGPT 4 create a new module implementation for this library

---

## Instructions for Implementing a New Module

1. Create a new Python file: `module_validator/modules/[MODULE_NAME]/[MODULE_NAME].py`

2. In this file, implement a `process` function with the following signature:
   ```python
   def process(data: Union[str, Dict[str, Any]], params: Dict[str, Any]) -> Any:
       # Implementation here
       pass
   ```

3. Add any necessary imports and helper functions in the same file.

4. Update `setup.py` to include the new module as an entry point:
   ```python
   setup(
       # ...
       entry_points={
           # ...
           "module_validator.inference": [
               # ...
               "[MODULE_NAME] = module_validator.modules.[MODULE_NAME].[MODULE_NAME]:process"
           ],
       },
       # ...
   )
   ```

5. If needed, create a configuration file: `module_validator/config/[ENVIRONMENT]/[MODULE_NAME].yaml`

6. Update `module_validator/main.py` to use the new module:
   ```python
   [MODULE_NAME]_process = registry.get_module('[MODULE_NAME]')
   if [MODULE_NAME]_process:
       result = [MODULE_NAME]_process(input_data, config.get_config('[MODULE_NAME]').get('[MODULE_NAME]', {}))
       print(f"[MODULE_NAME] result: {result}")
   ```

7. Reinstall the package:
   ```
   pip install -e .
   ```

8. Test the new module by running:
   ```
   python module_validator/main.py
   ```

Remember to replace `[MODULE_NAME]` with the actual name of your new module, and `[ENVIRONMENT]` with the appropriate environment (e.g., 'development', 'production').

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.