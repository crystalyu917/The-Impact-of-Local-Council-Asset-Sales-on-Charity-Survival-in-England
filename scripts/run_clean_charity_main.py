import sys
import os
import pandas as pd

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleaning.clean_charity_main import clean_charity_main

if __name__ == '__main__':
    charity = pd.read_csv('data/raw/charities_RegisteredCharitiesInEnglandAndWales2025.csv', low_memory=False)
    company_house = pd.read_csv('data/raw/companyHouseData2025.csv', low_memory=False)
    charity_web = pd.read_csv('data/raw/registeredCharityDataFromWeb.csv', low_memory=False)
    postcodes = pd.read_csv('data/raw/match_postcode_ONSPD2025.csv', low_memory=False)
    local_authority = pd.read_csv('data/raw/local_authority_names_and_codes_ONSPD2023.csv', low_memory=False)
    category = pd.read_csv('data/raw/charityClassification_RegisteredCharitiesInEnglandAndWales2025.csv', low_memory=False)

    df = clean_charity_main(charity, company_house, charity_web, postcodes, local_authority, category)
    df.to_csv('data/processed/charity_main_cleaned.csv', index=False)

    print("✅ Cleaned dataset saved to: data/processed/charity_main_cleaned.csv")
