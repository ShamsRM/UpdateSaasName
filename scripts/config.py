# Constants: keywords, thresholds, etc.

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
  "website" :  "https://notion.so",
  "editor" : "..."
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