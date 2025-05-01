
#B) Detect new names of SaaS, update the existing ones, and remove potential duplicates.
from difflib import SequenceMatcher

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def detect_updates(domain_dict):
    updated_dict = {}
    for domain, data in domain_dict.items():
        print("Checking updates for ",domain,"...")
        
        # --- Mock detection logic ---
        # In production, you might call Crunchbase, Clearbit, etc.

        # Simulate a name or editor change
        if "notionlabs.com" in domain:
            data["editor"] = "Notion Labs"  # Simulated correction
            data["aliases"].append("Notion Labs Inc.")

        updated_dict[domain] = data
    return updated_dict

# 2. Merge duplicates
def deduplicate_domains(domain_dict):
    cleaned_dict = {}
    seen = {}

    for domain, data in domain_dict.items():
        matched = False
        for key, existing in cleaned_dict.items():
            if is_similar(data["name"], existing["name"]) or any(is_similar(alias, existing["name"]) for alias in data.get("aliases", [])):
                # Merge aliases
                existing["aliases"] = list(set(existing["aliases"] + data.get("aliases", [])))
                matched = True
                break

        if not matched:
            cleaned_dict[domain] = data
    return cleaned_dict