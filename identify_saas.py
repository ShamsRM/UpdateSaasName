import pandas as pd # type: ignore
from collections import defaultdict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


VISIT_COUNT_THRESH = 1 #30
DISTINCT_USERS_THRESH = 1 #10

URL_VISIT_DATA = {
    "user_id": ["u1", "u2", "u1", "u3", "u1"],
    "url": [
        "https://notion.so",
        "https://notion.so",
        "https://codesandbox.io",
        "https://medium.com",
        "https://meta.com"],
    "timestamp": [
        "2025-04-23T11:00:00Z",
        "2025-04-22T10:00:00Z",
        "2025-04-21T09:00:00Z",
        "2025-04-20T07:00:00Z",
        "2025-04-20T07:00:00Z"
    ]
}


EXISTING_DOMAINS = { "notion.so" : 
  {"name": "Notion",
  "aliases": ["Notion Labs", "Notion.so"],
  "website" :  "https://notion.so"
  }}

CRUNCHBASE_API_KEY = "your_crunchbase_api_key"

WEBSITE_KEYWORDS = {
    "onboarding": ["sign up", "get started", "free trial", "try it free", "request demo"],
    "pricing": ["pricing", "plans", "subscription", "billing"],
    "login": ["login", "sign in", "access your account"],
    "product": ["features", "dashboard", "platform", "cloud"],
    "cta": ["start for free", "start trial"]
}

WIKIPEDIA_KEYWORDS = ["saas", "software as a service", "cloud", "web application", "cloud-based", "online platform"]

CRUNCHBASE_KEYWORDS = ["saas", "software", "cloud", "enterprise", "subscription", "web", "devops"]

WEBSITE_CATEGORY_WEIGHTS = {
    "onboarding": 2,
    "pricing": 1.5,
    "login": 1,
    "product": 1,
    "cta": 2
}

#A) SaaS Identification

#1) URL parsing

def clean_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # remove classical subdomains
        parts = domain.split('.')
        if len(parts) > 2:
            domain = '.'.join(parts[-2:])
        return domain
    except:
        return None

#def remove_existing_domains(url):

def domain_to_root_url(domain):
    """
    Convert a domain (e.g., 'codesandbox.io') to a full root URL (e.g., 'https://codesandbox.io').

    :param domain: The domain name (e.g., 'codesandbox.io')
    :return: The full root URL (e.g., 'https://codesandbox.io')
    """
    # Ensure the domain is not empty and strip any leading/trailing spaces
    domain = domain.strip()
    
    # Check if the domain already has a protocol (http or https)
    if not domain.startswith(('http://', 'https://')):
        # If no protocol is found, prepend 'https://'
        domain = 'https://' + domain
    
    # Return the URL with the domain as the root URL
    return domain


#2) APIs
#a) Wikipedia
def get_wikipedia_score(url_or_name, saas_keywords=WIKIPEDIA_KEYWORDS):

    # Step 1: clean domain name or brand
    domain = url_or_name.replace("https://", "").replace("www.", "").split("/")[0]
    search_term = domain.split(".")[0]  # crude brand extractor
    
    # Step 2: search Wikipedia
    search_url = f"https://en.wikipedia.org/w/api.php"
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



#b) Crunchbase
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


#3) Website

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

        return normalized_score

    except Exception as e:
        print(f"[ERROR] Failed to compute website keyword score for {url}: {e}")
        
        # If use_fallback is True, you can return a default score if the website can't be fetched
        if use_fallback:
            print(f"[INFO] Using fallback score for {url}.")
            return 0.0

        # Optionally, you could raise the error again if no fallback is desired
        raise e

#B) 1) Combine SaaS scores

def compute_total_saas_score(wiki, crunch, website, weights=(1, 1, 1)):
    w1, w2, w3 = weights
    return round(wiki * w1 + crunch * w2 + website * w3/3, 2)

    if total_saas_score > total_threshold :
        return True
    else :
        return False

#2) Get SaaS name and aliases
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

def run_weekly_saas_identification(urls_df : pd.DataFrame, existing_domains_dict : dict ) : 
    # I) Weekly identification of SaaS in visited URLs : 1) frequency of visit, 2) cross with company APIs (Wikipedia, Crunchbase, Linkedin), 3) Website keywords (“page login", "pricing", "try (for) free”)

    #0) Get URL
    #Limitations : get the generic URL

    urls_df["Domain"] =  urls_df["url"].apply(clean_domain)
    #Check if domain is already in existing_domains, if so, remove it from the dataset.
    urls_df["Existing_Domain"]=urls_df["Domain"].apply(lambda x : True if x in existing_domains_dict else False)
    urls_df = urls_df[urls_df["Existing_Domain"] == False]
    urls_df.drop(columns=["Existing_Domain"],inplace=True)


    # 1) Frequency of visit : at least 30 total visits, from 10 different users in the last week
    #Improvement : return a confidence score between 0 and 1, depending on the relative visits on the url vs the other SaaS, and the number of different users vs the other SaaS.
    #Then set a threshold (ex : 0.5)

    #Aggregate by number of visits and distinct users
    agg_df = urls_df.groupby("Domain").agg(
        total_visits=("user_id", "count"),
        unique_users=("user_id", pd.Series.nunique)).reset_index()

    #Filter with threshold
    filtered_df = agg_df[(agg_df["total_visits"] >= VISIT_COUNT_THRESH) & (agg_df["unique_users"] >= DISTINCT_USERS_THRESH)]

    #2) API data

    #a) Wikipedia score : search for keywords ("software", "cloud", "platform") in the intro of the related Wiki page
    #Limitations : keywords to search for, infos outside of the intro, other edge cases (ex : a website that talks about software), wrong matching with the Wiki page / company not found
    filtered_df["Wiki_Saas_score"] = filtered_df["Domain"].apply(get_wikipedia_score)

    #b) Crunchbase score : look for keywords ("saas", "cloud computing", "b2b", "platform", "software") on the company Crunchbase page categories
    #Limitations : paid API, keywords to search for, wrong matching with the Crunchbase page / company not found

    filtered_df["Crunchbase_Saas_score"] = filtered_df["Domain"].apply(get_crunchbase_score)
    #c) Linkedin score : ...

    #3) Website keyword data score
    #Limitations : keywords only in English (extend to other languages of the organisation),  use url paths as well (ex : "site.com/pricing"), Weight by frequency: More mentions = stronger confidence

    filtered_df["root_url"] = filtered_df["Domain"].apply(domain_to_root_url)
    filtered_df["Website_Saas_score"] = filtered_df["root_url"].apply(get_website_score)

    #B) Detect new names of SaaS. 1) Compute total score 2) Get infos associated with domain (name, aliases, urls), Check if is not an old SaaS (similarity score), if so add these elements to the list, if not, add a new SaaS

    #1) Compute total SaaS score
    filtered_df["total_saas_score"] = filtered_df.apply(lambda row: compute_total_saas_score(row["Wiki_Saas_score"], row["Crunchbase_Saas_score"], row["Website_Saas_score"]),axis=1)
    print("url SaaS scores : ", filtered_df[["root_url","Wiki_Saas_score", "Website_Saas_score" , "total_saas_score"]])
    #filtered_df = filtered_df[filtered_df["total_saas_score"] >= 0.5]

    
    #2) Get infos associated with domain and add to the existing domains info
    for index, row in filtered_df.iterrows():
        domain = row["Domain"]
        website = row["root_url"]
        name = get_saas_name_from_wikipedia(domain)
        aliases = get_aliases_from_wikipedia(domain)

        existing_domains_dict[domain] = {"name" : name, 
                                    "aliases": aliases, 
                                    "website" : website,
                                    "saas_confidence_score" : row["total_saas_score"] }

    #C) Check SaaS changinexisting SaaS similarities and new names (especially for the old ones).
