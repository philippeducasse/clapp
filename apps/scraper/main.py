from fastapi import FastAPI
import httpx
import os
from dotenv import load_dotenv
import yaml

load_dotenv()

app = FastAPI()

CLAPP_API_URL = os.getenv("CLAPP_API_URL")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/fetch-schema")
async def read_item():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CLAPP_API_URL}/api/schema/")
        schema = yaml.safe_load(response.text)

    return schema