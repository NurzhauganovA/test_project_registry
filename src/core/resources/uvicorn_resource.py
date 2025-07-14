import uvicorn
from fastapi import FastAPI


def uvicorn_server_resource(app: FastAPI, host: str, port: int, debug: bool):
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="debug" if debug else "info",
        reload=False,  # ❗️Disable reload, since it is already in watchfiles
    )
    server = uvicorn.Server(config)

    return server
