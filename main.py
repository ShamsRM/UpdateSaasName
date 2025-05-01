import pandas as pd # type: ignore

from identify_saas import (
    EXISTING_DOMAINS,
    URL_VISIT_DATA,
    run_weekly_saas_identification
)


def main():
    urls_df = pd.DataFrame(URL_VISIT_DATA)
    urls_df["timestamp"] = pd.to_datetime(urls_df["timestamp"])
    print('EXISTING_DOMAINS : ', EXISTING_DOMAINS)
    run_weekly_saas_identification(urls_df, EXISTING_DOMAINS)
    print('Updated Domains : ', EXISTING_DOMAINS)


if __name__ == "__main__":
    main()