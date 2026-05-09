from fastapi import FastAPI
import httpx
import os
from dotenv import load_dotenv
import yaml
from pydantic import BaseModel
from schemas.schemas import ScrapedFestival
from parser import parse_buskers_central
load_dotenv()

app = FastAPI()

CLAPP_API_URL = os.getenv("CLAPP_API_URL")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/fetch-schema")
async def fetch_clapp_schema():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CLAPP_API_URL}/api/schema/")
        schema = yaml.safe_load(response.text)

    return schema

class ScrapeRequest(BaseModel):
    url: str

@app.post("/basic-scrape")
async def basic_scrape(request: ScrapeRequest) -> list[ScrapedFestival]:
    async with httpx.AsyncClient() as client:
        response = await client.get(request.url)
        last_modified = response.headers.get("last_modified")

        print(f"Last modified: {last_modified}")
        festivals = parse_buskers_central(response.text)
        print(festivals)

    return festivals

