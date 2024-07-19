import json
import ast
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

CODE_PATH = os.getenv("CODE_PATH")
FUNCTION_PATH = os.getenv("FUNCTION_PATH")


def extract_function_calls(code):
    class FunctionCallVisitor(ast.NodeVisitor):
        def __init__(self):
            """
            Extracts function calls from the given code by parsing the Abstract Syntax Tree (AST) of the code.

            Args:
                code (str): The code to extract function calls from.

            Returns:
                list: A list of tuples containing the function name, the called function, and the arguments passed to the function.
            """
            self.results = []

        def visit_FunctionDef(self, node):
            """
            Visits a function definition node in the abstract syntax tree (AST) and extracts function calls
            made within the function. The function name, the called function, and the arguments passed to the
            function are stored in a list.

            Args:
                node (ast.FunctionDef): The function definition node to visit.

            Returns:
                None
            """
            functionname = node.name
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and (
                        isinstance(child.func.value, ast.Name)
                        and child.func.value.id == "self"
                    )
                ):
                    args = []
                    for arg in child.args:
                        if isinstance(arg, ast.Constant):
                            args.append(repr(arg.value))
                        elif isinstance(arg, ast.Name):
                            args.append(arg.id)
                    for kwarg in child.keywords:
                        if isinstance(kwarg.value, ast.Constant):
                            ast_constant_name = f"{kwarg.arg}={repr(kwarg.value)}"
                            if "ast.Constant object at" in ast_constant_name:
                                ast_constant_name = (
                                    f"{kwarg.arg}={repr(kwarg.value.value)}"
                                )
                            args.append(ast_constant_name)
                        elif isinstance(kwarg.value, ast.Name):
                            args.append(f"{kwarg.arg}={kwarg.value.id}")
                    calledfunction = child.func.attr
                    self.results.append((functionname, calledfunction, args))

    tree = ast.parse(code)
    visitor = FunctionCallVisitor()
    visitor.visit(tree)
    return visitor.results


def construct_function_map(code_path, save_path):
    """
    Constructs a map of function names to their corresponding called functions and arguments
    from the provided code file and saves the map to a specified path.

    Args:
        code_path (str): The path to the code file to extract function calls from.
        save_path (str): The path where the constructed function map will be saved.

    Returns:
        None
    """
    with open(code_path, "r", encoding="utf-8") as f:
        code = f.read()
    results = extract_function_calls(code)

    function_dict = {}
    for function in results:
        functionname, calledfunction, args = function
        function_dict[functionname] = {"function": calledfunction, "arguments": args}

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(function_dict, indent=4))


if __name__ == "__main__":
    filepath = Path(CODE_PATH)
    results = extract_function_calls(filepath.read_text())
    for result in results:
        function_name, called_function, arguments = result

    save_path = Path(FUNCTION_PATH)

    construct_function_map(CODE_PATH, FUNCTION_PATH)
