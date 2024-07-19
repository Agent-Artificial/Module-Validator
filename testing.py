import requests
import base64


def install_module(module_config: ModuleConfig):
        try:
            response = requests.get(
                f"{module_config.module_url}/modules/{module_config.module_name}",
                timeout=30,
            )
            response.raise_for_status()
            setup_file = response.text
            with open(
                f"modules/{module_config.module_name}/setup_{module_config.module_name}.py",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(base64.b64decode(setup_file).decode("utf-8"))
        except requests.RequestException as e:
            print(f"Error requesting module: {e}")