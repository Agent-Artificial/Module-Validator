import os
import sys
import argparse
from pathlib import Path


def set_working_directory_to_submodule(submodule_path):
    # Get the full path of the current script (which should be in the project root)
    project_root = os.path.dirname(Path.cwd() / "module_validator")

    # Construct the full path to the submodule
    submodule_full_path = os.path.join(project_root, submodule_path)

    # Verify that the submodule path exists
    if not os.path.exists(submodule_full_path):
        raise FileNotFoundError(f"Submodule path not found: {submodule_full_path}")

    # Change the current working directory
    os.chdir(submodule_full_path)

    # Add the submodule directory to sys.path to allow imports
    if submodule_full_path not in sys.path:
        sys.path.insert(0, submodule_full_path)

    print(f"Working directory set to: {os.getcwd()}")


def add_args(parser):
    parser.add_argument(
        "--path",
        type=str,
        default="module_validator/subnet_modules/bittensor_subnet_template",
    )

    return parser.parse_args()


def main(parser):
    args = add_args(parser)
    set_working_directory_to_submodule(args.path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    main(parser)
