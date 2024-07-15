import os
import json
import ast
import uvicorn
import importlib
import markdown2
import asyncio
from contextlib import asynccontextmanager
from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv


load_dotenv()

FUNCTION_DATA = {}
MARKDOWN_CONTENT = ""

def extract_function_info(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_info = {
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'parameters': [],
                'returns': None,
                'file_path': file_path
            }

            for arg in node.args.args:
                param = {'name': arg.arg, 'type': None}
                if arg.annotation:
                    param['type'] = ast.unparse(arg.annotation)
                function_info['parameters'].append(param)

            if node.returns:
                function_info['returns'] = ast.unparse(node.returns)

            functions.append(function_info)

    return functions

def walk_directory(directory: str) -> Dict[str, Dict[str, Any]]:
    result = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    functions = extract_function_info(file_path)
                    for func in functions:
                        result[func['name']] = func
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    return result

def generate_markdown(data: Dict[str, Dict[str, Any]]) -> str:
    md = "# Python Functions Documentation\n\n"
    for func_name, func_info in data.items():
        md += f"**`{func_name}`**\n\n"
        if func_info['docstring']:
            md += f"## **Docstring:**\n```\n{func_info['docstring']}\n```\n\n"
        md += "## **Parameters:**\n"
        if func_info['parameters']:
            for param in func_info['parameters']:
                param_type = f": `{param['type']}`" if param['type'] else ""
                md += f"- `{param['name']}`{param_type}\n"
        else:
            md += "None\n"
        md += "\n"
        returns = func_info['returns'] or "None specified"
        md += f"## **Returns:** `{returns}`\n\n"
        md += "---\n\n"
    return md


@asynccontextmanager
async def lifespan(app: FastAPI):
    directory = os.getenv("FUNCTIONS_DIRECTORY")
    data_dir = os.getenv("DATA_DIRECTORY")

    if not directory or not data_dir:
        logger.error("FUNCTIONS_DIRECTORY or DATA_DIRECTORY not set in .env file")
        return

    if not os.path.exists(directory):
        logger.error(f"FUNCTIONS_DIRECTORY {directory} does not exist")
        return

    if not os.path.exists(data_dir):
        logger.error(f"DATA_DIRECTORY {data_dir} does not exist")
        return

    FUNCTION_DATA = walk_directory(directory)

    # Save function data to a JSON file
    try:
        with open(os.path.join(data_dir, "function_data.json"), "w", encoding="utf-8") as f:
            json.dump(FUNCTION_DATA, f, indent=2)
        logger.info(f"Function data saved to {os.path.join(data_dir, 'function_data.json')}")
    except Exception as e:
        logger.error(f"Error saving function data: {str(e)}")

    # Generate markdown content
    MARKDOWN_CONTENT = generate_markdown(FUNCTION_DATA)

    # Save markdown to a file
    try:
        with open(os.path.join(data_dir, "function_docs.md"), "w", encoding="utf-8") as f:
            f.write(MARKDOWN_CONTENT)
        logger.info(f"Markdown content saved to {os.path.join(data_dir, 'function_docs.md')}")
    except Exception as e:
        logger.error(f"Error saving markdown content: {str(e)}")
    yield 
    
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def serve_spa():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python Functions Documentation</title>
        <script src="https://unpkg.com/htmx.org@1.9.6"></script>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
          tailwind.config = {
            theme: {
              extend: {
                colors: {
                  'dark': '#242a4e',
                  'light': '#d4d3d3',
                  'accent': '#802dad',
                  'primary': '#46baae',
                  'secondary': '#bbbb40',
                  'tertiary': '#a34242',
                  'quaternary': '#262626',
                }
              }
            }
          }
        </script>
    </head>
    <body class="bg-dark text-light">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-4xl font-bold text-primary mb-8">Python Functions Documentation</h1>
            <div id="content" hx-get="/markdown" hx-trigger="load" class="bg-quinary p-8 rounded shadow"></div>
        </div>
    </body>
    </html>
    """


@app.get("/markdown", response_class=HTMLResponse)
async def serve_markdown():
    with open("static/function_docs.md", "r", encoding="utf-8") as f:
        MARKDOWN_CONTENT = f.read()
    html_content = markdown2.markdown(MARKDOWN_CONTENT, extras=["fenced-code-blocks"])
    return f"""
              <br />
                <div class="markdown-body">{html_content}</div>"""


@app.get("/")
async def get_function_data():
    return FUNCTION_DATA


class FunctionParams(BaseModel):
    params: Dict[str, Any]
    

app.mount("/static", StaticFiles(directory="static"), name="static")
    
    
@app.post("/api/{function_name}")
async def execute_function(function_name: str, params: FunctionParams):
    if function_name not in FUNCTION_DATA:
        raise HTTPException(status_code=404, detail="Function not found")
    
    func_info = FUNCTION_DATA[function_name]
    file_path = func_info['file_path']
    
    # Import the module dynamically
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Get the function from the module
    func = getattr(module, function_name)
    
    # Execute the function with the provided parameters
    try:
        result = func(**params.params)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

if __name__ == "__main__":
    uvicorn.run("api.api:app", host="0.0.0.0", port=7575, reload=True)