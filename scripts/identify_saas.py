# -*- coding: utf-8 -*-

import pandas as pd  # type: ignore
import logging

from scripts.domain_utils import clean_domain, domain_to_root_url
from scripts.extract_info import get_aliases_from_wikipedia, get_saas_name_from_wikipedia
from scripts.scoring import compute_total_saas_score, get_crunchbase_score, get_website_score, get_wikipedia_score

VISIT_COUNT_THRESH = 1 #30
DISTINCT_USERS_THRESH = 1 #10



def run_saas_identification(urls_df , existing_domains_dict ) : 
    # I) Weekly identification of SaaS in visited URLs : 1) frequency of visit, 2) cross with company APIs (Wikipedia, Crunchbase, Linkedin), 3) Website keywords (“page login", "pricing", "try (for) free”)

    #0) Get URL
    #Limitations : get the generic URL

    urls_df["Domain"] =  urls_df["url"].apply(clean_domain)

    print('\n',"Detected domains : ", urls_df["Domain"].unique(), '\n')

    #Check if domain is already in existing_domains, if so, remove it from the dataset.
    urls_df["Existing_Domain"]=urls_df["Domain"].apply(lambda x : True if x in existing_domains_dict else False)
    urls_df = urls_df.loc[urls_df["Existing_Domain"] == False]
    urls_df.drop(columns=["Existing_Domain"],inplace=True)

    print("New domains : ", urls_df["Domain"].unique(), '\n')

    # 1) Frequency of visit : at least 30 total visits, from 10 different users in the last week
    #Improvement : return a confidence score between 0 and 1, depending on the relative visits on the url vs the other SaaS, and the number of different users vs the other SaaS.
    #Then set a threshold (ex : 0.5)

    #Aggregate by number of visits and distinct users
    agg_df = urls_df.groupby("Domain").agg(
        total_visits=("user_id", "count"),
        unique_users=("user_id", pd.Series.nunique)).reset_index()

    #Filter with threshold
    filtered_df = agg_df[(agg_df["total_visits"] >= VISIT_COUNT_THRESH) & (agg_df["unique_users"] >= DISTINCT_USERS_THRESH)]

    print("After filtering by frequency of visits : ", filtered_df["Domain"].unique(), '\n')


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

    #4) Compute total SaaS score
    filtered_df["total_saas_score"] = filtered_df.apply(lambda row: compute_total_saas_score(row["Wiki_Saas_score"], row["Crunchbase_Saas_score"], row["Website_Saas_score"]),axis=1)
    print('\n', filtered_df[["root_url","Wiki_Saas_score", "Website_Saas_score" , "total_saas_score"]], '\n')
    #filtered_df = filtered_df[filtered_df["total_saas_score"] >= 0.5]

    
    #5) Get infos associated with domain and add to the existing domains info
    for index, row in filtered_df.iterrows():
        domain = row["Domain"]
        website = row["root_url"]
        name = get_saas_name_from_wikipedia(domain)
        aliases = get_aliases_from_wikipedia(domain)

        existing_domains_dict[domain] = {"name" : name, 
                                    "aliases": aliases, 
                                    "website" : website,
                                    "saas_confidence_score" : row["total_saas_score"] }
    return existing_domains_dict
    #print('\n', existing_domains_dict, '\n')