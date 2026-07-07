
from fastapi import FastAPI

import logfire

app = FastAPI()

logfire.configure()
logfire.instrument_fastapi(app)


@app.get("/")
def read_root():
    logfire.info("Handling root request")
    return {"message": "Hello World"}