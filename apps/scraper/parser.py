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

def parse_open_street(html:str) -> list[ScrapedFestival]:
    soup = BeautifulSoup(html, 'html.parser')
    festivals = []

    for bold in soup.find_all('b'):
        name = bold.text.strip()
        
        # Skip headers
        if len(name) > 50 or name.isupper():
            continue
        
        # Get text after </b> until first semicolon
        next_text = bold.next_sibling
        if isinstance(next_text, str):
            # Extract location: "; City (Country); ..."
            location_part = next_text.split(';')[1].strip()
            location_part = location_part.lstrip('; ')
            
            # Parse "City (Country)"
            if '(' in location_part and ')' in location_part:
                town = location_part.split('(')[0].strip()
                country = location_part.split('(')[1].split(')')[0].strip()
            else:
                town = location_part
                country = ""
        else:
            town = country = ""
        
        # Find next <a> tag
        link = bold.find_next('a')
        if link and link.get('href'):
            url = link.get('href').strip()
            festivals.append(ScrapedFestival(
                name=name,
                website_url=url,
                town=town,
                country=country
            ))

    return festivals