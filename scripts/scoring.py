# Functions to compute Wikipedia, Crunchbase, Website keyword scores

from collections import defaultdict
from bs4 import BeautifulSoup
import requests
from scripts.config import CRUNCHBASE_API_KEY, CRUNCHBASE_KEYWORDS, WEBSITE_CATEGORY_WEIGHTS, WEBSITE_KEYWORDS, WIKIPEDIA_KEYWORDS


def get_wikipedia_score(url_or_name, saas_keywords=WIKIPEDIA_KEYWORDS):

    # Step 1: clean domain name or brand
    domain = url_or_name.replace("https://", "").replace("www.", "").split("/")[0]
    search_term = domain.split(".")[0]  # crude brand extractor
    
    # Step 2: search Wikipedia
    search_url = f"https://en.wikipedia.org/w/api.php"  # noqa: F541
    params = {
        "action": "query",
        "list": "search",
        "srsearch": search_term,
        "format": "json"
    }

    try:
        search_res = requests.get(search_url, params=params).json()
        if not search_res["query"]["search"]:
            return 0.0  # no Wikipedia result
        
        # Step 3: get page content of top result
        page_title = search_res["query"]["search"][0]["title"]
        page_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
        page_res = requests.get(page_url).json()
        text = (page_res.get("extract") or "").lower()

        # Step 4: keyword match scoring
        score = sum(1 for kw in saas_keywords if kw in text) / len(saas_keywords)
        return round(score, 2)
    except:
        return 0.0


#not working, need an API key
def get_crunchbase_score(domain, api_key = CRUNCHBASE_API_KEY, saas_keywords=CRUNCHBASE_KEYWORDS):
    # Step 1: query Crunchbase API (example URL)
    url = "https://api.crunchbase.com/api/v4/entities/organizations"
    params = {
        "field_ids": ["categories", "description", "name"],
        "query": domain,
        "user_key": api_key
    }

    try:
        res = requests.get(url, params=params).json()
        if not res.get("entities"):
            return 0.0

        # Step 2: extract tags
        entity = res["entities"][0]
        fields = entity.get("properties", {})
        tags = (fields.get("categories") or []) + [fields.get("description", "")]
        text = " ".join([t.lower() for t in tags if isinstance(t, str)])

        # Step 3: compute score
        score = sum(1 for kw in saas_keywords if kw in text) / len(saas_keywords)
        return round(score, 2)
    except:
        return 0.0

def get_website_score(url, use_fallback=True):
    """
    Fetches website HTML, extracts text, and computes a SaaS likelihood score (0-1)
    based on presence of SaaS-related keywords and CTA patterns. If unable to fetch, falls back to a default score.
    """
    try:
        # Step 1: Fetch and parse HTML content
        res = requests.get(url, timeout=5)
        
        # Handle potential 403 error or any failed request
        if res.status_code == 403:
            print(f"[ERROR] Access denied to {url} (HTTP 403).")
            return 0.0

        # Parse HTML content if request was successful
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True).lower()
        print("website text : ", text[:1000])  # Print first 100 characters for debugging

        # Step 2: Score computation
        total_possible = sum(WEBSITE_CATEGORY_WEIGHTS.values())
        actual_score = 0
        keyword_hits = defaultdict(int)

        for category, keywords in WEBSITE_KEYWORDS.items():
            for word in keywords:
                if word in text:
                    actual_score += WEBSITE_CATEGORY_WEIGHTS[category]
                    keyword_hits[category] += 1
                    break  # Avoid double counting a category

        # Step 3: Normalize
        normalized_score = round(actual_score / total_possible, 2)
        print("website keyword hits : ", keyword_hits)  # Print first 100 characters for debugging

        return normalized_score

    except Exception as e:
        print(f"[ERROR] Failed to compute website keyword score for {url}: {e}")
        
        # If use_fallback is True, you can return a default score if the website can't be fetched
        if use_fallback:
            print(f"[INFO] Using fallback score for {url}.")
            return 0.0

        # Optionally, you could raise the error again if no fallback is desired
        raise e

def compute_total_saas_score(wiki, crunch, website, weights=(1, 1, 1)):
    w1, w2, w3 = weights
    return round(wiki * w1 + crunch * w2 + website * w3/3, 2)