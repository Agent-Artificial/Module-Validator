   
def main():
    if len(sys.argv) < 2:
        print("Usage: python config_extractor.py <path_to_config_file>")
        sys.exit(1)

    file_dir = sys.argv[1]
    all_arguments = {}
    for root, dirs, files in os.walk(file_dir):
        for dir in dirs:
            if dir.startswith("__"):
                continue
        for file in files:
            if file.startswith("__") or file.endswith(".pyc"):
                continue                                    
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r') as f:
                    document = f.read()
                if "add_argument" not in document:
                    continue
                file_path = os.path.join(root, file)
                arguments = extract_argparse_arguments(file_path)
                if len(arguments) <= 0:
                    continue
                
                for argument in arguments:
                    if 'default' not in argument:
                        argument["default"] = f"no default value"
                    if "type" not in argument:
                        argument["type"] = "str"
                    if "help" not in argument:
                        argument["help"] = f"Commandline argument for {argument['name']}"
                    if "name" in argument:
                        all_arguments[argument["name"]] = argument