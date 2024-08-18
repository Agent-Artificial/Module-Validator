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

    parser_pattern = re.compile(r'(def\s+\w+add\w*args\w*\(.*?\):.*?)(return.*?parser)', re.DOTALL)
    new_content = "\n        ".join(parser_lines)
    return parser_pattern.sub(fr'\1\n        {new_content}\n        \2', document2)
    
    
def parse_and_add_arguments(document1, document2):
    args_matches = find_arguments(document1)
    # Process extracted arguments
    new_env_vars = []
    for arg, default in args_matches:
        var_name = arg.strip('--').upper().replace('.', '_')
        default_value = default.strip('"\'') if default != 'None' else None
        new_var_key = f"{var_name}="
        new_var_value = input(f'Enter value for {var_name}[{default_value}]: ') or default_value
        new_env_vars.append(f'\"{new_var_key}{new_var_value}\"')

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
    existing_lines = lines_match.group(2).strip().split(',\n')
    existing_lines = [line.strip() for line in existing_lines if line.strip()]

    # Combine new and existing environment variables, avoiding duplicates
    combined_lines = existing_lines + [line for line in new_env_vars if line not in existing_lines]
    print(combined_lines)
    # Create the updated function content
    updated_lines = ',\n            '.join(combined_lines)
    updated_function = function_content.replace(
        lines_match.group(0),
        f'{lines_match.group(1)}\n            {updated_lines}\n        ]'
    )
    print(updated_function)
    # Replace the old function with the updated one in document2
    updated_document2 = document2.replace(function_content, updated_function)
    return updated_document2


if __name__ == "__main__":
    target_config = os.getenv("target_config") or input("Enter the name of the target config file['module_validator/chain/bittensor_subnet_template/template/utils/config.py']: ") or "module_validator/chain/bittensor_subnet_template/template/utils/config.py"
    modify_configuration_file  = os.getenv("modify_configuration_file") or input("Enter the path to the modify configuration file['utils/configuration.py']: ") or "utils/configuration.py"
    with open(target_config, "r", encoding="utf-8") as f:
        document1 = f.read()
    with open(modify_configuration_file, "r", encoding="utf-8") as f:
        document2 = f.read()
    new_document = parse_and_add_arguments(document1, document2)
    print(new_document)
    final_doc = parse_and_add_parser_arguments(document1, new_document)
    with open(modify_configuration_file, "w", encoding="utf-8") as f:
        f.write(final_doc)
    print(final_doc)        
    