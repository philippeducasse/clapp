from fastapi import FastAPI
import httpx
import os
from dotenv import load_dotenv
import yaml
from pydantic import BaseModel
from schemas.schemas import ScrapedFestival
from parser import parse_buskers_central, parse_open_street
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

@app.post("/buskerscentral")
async def scrape_buskers_central(request: ScrapeRequest) -> list[ScrapedFestival]:
    async with httpx.AsyncClient() as client:
        response = await client.get(request.url)
        festivals = parse_buskers_central(response.text)

    return festivals

@app.post("/openstreet")
async def scrape_open_street(request: ScrapeRequest) -> list[ScrapedFestival]:
    async with httpx.AsyncClient() as client:
        response = await client.get(request.url)
        festivals = parse_open_street(response.text)

    return festivals

