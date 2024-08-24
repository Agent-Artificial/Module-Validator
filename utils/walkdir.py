import os

# Set the directory to start from
start_dir = "."

# Create or open the output file
with open("utils/output.txt", "w", encoding="utf-8") as output_file:
    # Walk through the directory and subdirectories
    for dirpath, dirnames, filenames in os.walk(start_dir):
        # Loop over the files in the current directory
        for filename in filenames:
            # Check if the file is a Python file
            if filename.endswith(".py"):
                # Construct the full file path
                file_path = os.path.join(dirpath, filename)
                if file_path.startswith("./.venv"):
                    continue

                # Open the Python file and read its contents
                with open(file_path, "r", encoding="utf-8") as py_file:
                    contents = py_file.read()

                # Write the file contents to the output file
                output_file.write(f"File: {file_path}\n\n")
                output_file.write(contents)
                output_file.write("\n\n")
