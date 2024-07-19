import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
import markdown2

from bittensor import ALL_COMMANDS as cli_structure
from bittensor.axon import FastAPIThreadedServer, AxonMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_markdown():
    md_content = "# API Documentation\n\n"
    
    for main_command, details in cli_structure.items():
        md_content += f"## {main_command.capitalize()}\n\n"
        md_content += f"**Endpoint:** `/{main_command}`\n\n"
        md_content += f"**Description:** {details.get('help', 'No description available.')}\n\n"
        md_content += "**Aliases:** " + ", ".join(details.get('aliases', [])) + "\n\n"
        md_content += "### Sub-commands\n\n"
        
        for command_name in details.get('commands', {}):
            md_content += f"- `/{main_command}/{command_name}`\n"
        
        md_content += "\n"
    
    return md_content


def create_endpoint(path, command_info):
    @app.get(path)
    async def endpoint():
        function_info = None
        try:
            function_info = {
                "name": command_info.get('name', ''),
                "aliases": command_info.get('aliases', []),
                "help": command_info.get('help', ''),
                "available_commands": list(command_info.get('commands', {}).keys())
            }
        except HTTPException as e:
            return {"error": str(e), "message": f"Unable to get command info. {function_info}", "status_code": e.status_code}
        return {"data": function_info, "status_code": 200}


def create_command_endpoint(path, command_name, command_class):
    command_name = command_name.replace("_", "-")
    command_class = command_class
    @app.get(path)
    async def command_endpoint():
        function_info = None
        try:
            function_info = {
                "command": command_name,
                "class": str(command_class)
            }
        except HTTPException as e:
            return {"error": str(e), "message": f"Unable to execute command. {function_info}", "status_code": e.status_code}
        return {"data": function_info, "status_code": 200}


# Create main endpoints and sub-endpoints
for main_command, details in cli_structure.items():
    main_path = f"/{main_command}"
    create_endpoint(main_path, details)
    
    for command_name, command_class in details.get('commands', {}).items():
        command_path = f"{main_path}/{command_name}"
        create_command_endpoint(command_path, command_name, command_class)


markdown_content = generate_markdown()


@app.get("/")
async def root():
    html_content = markdown2.markdown(markdown_content)
    return HTMLResponse(content=html_content, status_code=200)


@app.post("{main_path}/{command_name}")
async def execute_command(main_path, command_name, *args, **kwargs):
    result = None
    try:
        result = cli_structure[main_path][command_name](*args, **kwargs)
    except HTTPException as e:
        return {"error": str(e), "message": f"Unable to execute command. {result}", "status_code": e.status_code}
    return {"data": result, "status_code": 200}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)