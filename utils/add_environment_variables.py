import argparse
import re
import os


def find_arguments(document):
    # Extract arguments from document1
    args_pattern = re.compile(r'parser\.add_argument\(\s*"(.*?)",\s*.*?default\s*=\s*(.*?)\s*[,\)]', re.DOTALL)
    return args_pattern.findall(document)


def parse_and_add_parser_arguments(document1, document2):
    args_matches = find_arguments(document1)
    parser_lines = []
    for args, default in args_matches:
        default_value = f'f\'{{os.getenv(\"{args.strip("--").upper().replace(".", "_")}\")}}\''
        parser_line = f"parser.add_argument('{args}', default={default_value})"
        parser_lines.append(parser_line)
    parser_lines = list(set(parser_lines))
    parser_pattern = re.compile(r'(def\s+\w+add\w*args\w*\(.*?\):.*?)(return.*?parser)', re.DOTALL)
    new_content = "\n        ".join(parser_lines)
    return parser_pattern.sub(fr'\1\n        {new_content}\n        \2', document2)
    
    
def parse_and_add_arguments(document1, document2):
    args_matches = find_arguments(document1)
    # Process extracted arguments
    new_env_vars = []
    for arg, default in args_matches:
        var_name = arg.strip('--').upper().replace('.', '_')
        default_value = var_name.strip('"\'').strip('f"{').strip("'").strip("f\'\'\'").strip('f\"\"\"').split("'")[0].split(" if")[0].lower()
        new_default_value = None
        if "." in default_value:
            new_default_value = default_value.split(".")[1]
        environment = os.environ.copy()
        if default_value in environment:
            var_name = default_value
            new_default_value = os.getenv(f"{var_name}")
        else:
            var_name = arg.strip('--').upper().replace('.', '_')
        if new_default_value is None:
            new_default_value = os.getenv(f"{var_name}")
        if new_default_value == default_value:
            new_default_value = "No default value"
        line = f'\"{var_name}={new_default_value}\",'
        new_env_vars.append(line)


    # Find the *add*_env_variables function in document2
    function_pattern = re.compile(r'def\s+(\w*add\w*env\w*variables\w*)\(.*?\):.*?return.*?lines', re.DOTALL)
    if not (function_match := function_pattern.search(document2)):
        raise ValueError("Could not find _add_env_variables function in document2")
    function_name = function_match.group(1)
    function_content = function_match.group(0)
    # Find the list of environment variables in the function
    lines_pattern = re.compile(r'(self\.lines\s*=\s*\[)([^\]]*)\]', re.DOTALL)
    if not (lines_match := lines_pattern.search(function_content)):
        raise ValueError(f"Could not find lines assignment in {function_name} function")
    existing_lines = lines_match.group(2).strip().split('\n             ')
    existing_lines = list(set([f"{line.strip()}," for line in existing_lines if line.strip()]))
    print("".join([f"{line}\n" for line in existing_lines]))
    existing_block = "\n            ".join(existing_lines)
    new_block = "\n            ".join(list(set(new_env_vars)))
    # Combine new and existing environment variables, avoiding duplicates
    combined_lines = existing_block + "\n            " + new_block
    print(combined_lines)
    
    updated_function = function_content.replace(
        lines_match.group(0),
        f'{lines_match.group(1)}\n            {combined_lines}\n        ]'
    )
    # Replace the old function with the updated one in document2
    updated_document2 = document2.replace(function_content, updated_function)
    return updated_document2

    
def main():
    base_file = "module_validator/chain/"
    source_file = input("Enter the name of the target config file['bittensor_subnet_template/template/utils/config.py']: ") or "bittensor_subnet_template/template/utils/config.py"
    source_path = base_file + source_file
    target_file = input("Enter the path to the modify configuration file['utils/configuration.py']: ") or "utils/configuration.py"
    with open(source_path, "r", encoding="utf-8") as f:
        document1 = f.read()
    with open(target_file, "r", encoding="utf-8") as f:
        document2 = f.read()
        
    updated_document2 = parse_and_add_arguments(document1, document2)
    # print(new_document)
    mirror_path = "utils/generated_config.py"
    with open(mirror_path, "w", encoding="utf-8") as f:
        f.write(updated_document2)


if __name__ == "__main__":
    main()