import pandas as pd # type: ignore

from scripts.identify_saas import run_saas_identification
from scripts.config import (
    EXISTING_DOMAINS,
    URL_VISIT_DATA,
)
from scripts.update_info import deduplicate_domains, detect_updates


def main():
    # Step 1: Detect new SaaS domains
    urls_df = pd.DataFrame(URL_VISIT_DATA)
    urls_df["timestamp"] = pd.to_datetime(urls_df["timestamp"])
    print('EXISTING_DOMAINS : ', EXISTING_DOMAINS)
    new_domains = run_saas_identification(urls_df, EXISTING_DOMAINS)

    # Step 2: Detect updates in existing SaaS domains
    updated_domains = detect_updates(new_domains)
    print('\n','Updated SaaS Domains : ', updated_domains)

    
    # Step 3: Deduplicate
    final_domains = deduplicate_domains(updated_domains)
    print('\n','Deduplicated SaaS Domains : ', final_domains)


if __name__ == "__main__":
    main()