

from bs4 import BeautifulSoup
import requests


def get_saas_name_from_wikipedia(wikipedia_slug: str) -> str:
    """
    Given a Wikipedia page slug, fetch the page and extract the main title (SaaS name).
    
    Args:
        wikipedia_slug (str): The slug of the Wikipedia page (e.g., 'Notion_(productivity_software)')
    
    Returns:
        str: The main title of the page (usually the SaaS or company name)
    """
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wikipedia_slug}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        title = data.get("title", "")
        return title
    except Exception as e:
        print(f"[ERROR] Failed to fetch SaaS name from Wikipedia for {wikipedia_slug}: {e}")
        return ""

def get_aliases_from_wikipedia(wikipedia_slug):
    url = f"https://en.wikipedia.org/wiki/{wikipedia_slug}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        infobox = soup.find("table", {"class": "infobox"})
        if not infobox:
            return []

        aliases = []
        for row in infobox.find_all("tr"):
            header = row.find("th")
            if header and header.get_text(strip=True).lower() in ["former name", "former names", "also known as", "trade name"]:
                data = row.find("td")
                if data:
                    alias_text = data.get_text(separator=",", strip=True)
                    alias_text = alias_text.split(",")  # in case of multiple
                    aliases.extend([a.strip() for a in alias_text if a.strip()])
        
        return aliases
    except Exception as e:
        print(f"[ERROR] Fetching aliases failed: {e}")
        return []