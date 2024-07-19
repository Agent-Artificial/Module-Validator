import os
import uvicorn

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from typing import Optional
from data_models import MinerConfig, BaseMiner, app


templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    """
    A function that handles the root GET request to the FastAPI application.

    This function is decorated with `@app.get("/")` which means it will be called when a GET request is made to the root URL of the application.

    Returns:
        TemplateResponse: A response object that renders the "index.html" template.
    """
    return templates.TemplateResponse("index.html")


def add_route(miner: BaseMiner, app: FastAPI):
    """
    A function to add a route to the specified miner with the given FastAPI app.

    Parameters:
    - miner: BaseMiner - The miner object to add the route to.
    - app: FastAPI - The FastAPI application to add the route to.

    Returns:
    - None
    """
    miner.add_route(miner, app)


def serve_miner(
    miner: BaseMiner, miner_config: MinerConfig, reload: Optional[bool] = True
):
    """
    Serves the miner with the specified miner configuration.

    Parameters:
    - miner: BaseMiner - The miner object to serve.
    - miner_config: MinerConfig - The configuration for the miner.
    - reload: Optional[bool] - Whether to reload the miner. Defaults to True.

    Returns:
    - None
    """
    miner.serve_miner(miner_config, reload=reload)


if __name__ == "__main__":
    uvicorn.run(
        "base.base_miner:app",
        host=os.getenv("MINER_HOST"),
        port=os.getenv("MINER_PORT"),
        reload=True,
    )
