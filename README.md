# Module Validator

Module Validator is a flexible Python package for dynamically loading and using inference modules, starting with an embedding function. It provides a simple interface for managing and utilizing various inference modules in your projects.

## Installation

You can install Module Validator using pip:

```bash
pip install module_validator
```

## Usage

## Configuration

Module Validator uses a flexible configuration system that supports different environments and module-specific settings.

### Directory Structure

Create a `config` directory in your project with the following structure:

```
module_validator/
    config/
        global_development.yaml
        global_production.yaml
        embedding_development.yaml
        embedding_production.yaml
        custom_module_development.yaml
        custom_module_production.yaml
```

### Configuration Files

1. Global configuration: `global_{environment}.yaml`
   Contains settings that apply to all modules.

2. Module-specific configuration: `{module_name}_{environment}.yaml`
   Contains settings specific to a particular module.

### Environment Selection

Set the `MODULE_VALIDATOR_ENV` environment variable to choose the configuration environment. If not set, it defaults to 'development'.

```bash
export MODULE_VALIDATOR_ENV=production
```

### Using Configurations in Modules

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

The `configure` method will be called automatically when the module is loaded, providing it with the merged global and module-specific configuration.


### Basic Usage

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

### Command Line Interface

Module Validator also provides a command-line interface:

```bash
module_validator list  # List all available modules
module_validator run embedding "sample text"  # Run the embedding module with input
```

## Extending Module Validator

You can extend Module Validator by adding your own inference modules. There are two ways to do this:

### 1. Creating a PyPI Package

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

### 2. Adding a Custom Module File

1. Create a Python file in the `custom_modules` directory of your project.
2. In this file, define a function named `inference`:

   ```python
   # my_custom_module.py
   def inference(input_text):
       # Your inference logic here
       return result
   ```

3. Module Validator will automatically detect and load this module.

## API Reference

### ModuleRegistry

The main class for managing inference modules.

#### Methods:

- `load_modules()`: Load all available modules from entry points and custom modules directory.
- `get_module(name)`: Get a specific module by name.
- `list_modules()`: List all available modules.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.