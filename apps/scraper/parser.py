from bs4 import BeautifulSoup
from schemas.schemas import ScrapedFestival

def parse_buskers_central(html:str) -> list[ScrapedFestival]:
    soup = BeautifulSoup(html, 'html.parser')
    festivals = []

    for link in soup.find_all('a', class_="song"):
        name = link.text.strip()
        url = link.get("href", "").strip()

        location_text = link.next_sibling
        if location_text:
            location = location_text.strip()
            parts = location.rsplit(',', 1)
            town = parts[0].strip() if parts else ""
            country = parts[1].strip() if len(parts) > 1 else ""
        else:
            town = country = ""
        
        festivals.append(ScrapedFestival(
            name=name,
            website_url=url,
            town=town,
            country=country
        ))

    return festivals