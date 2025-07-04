import sys
import os
import pandas as pd

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleaning.clean_council_housing import clean_council_housing

if __name__ == '__main__':
    council_housing_2023 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2023', skiprows=6)
    council_housing_2022 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2022', skiprows=6)
    council_housing_2021 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2021', skiprows=6)
    council_housing_2020 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2020', skiprows=6)
    council_housing_2019 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2019', skiprows=6)
    council_housing_2018 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2018', skiprows=6)
    council_housing_2017 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2017', skiprows=6)
    council_housing_2016 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2016', skiprows=6)
    council_housing_2015 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2015', skiprows=6)
    council_housing_2014 = pd.read_excel(r'data/raw/LAHS_sales_transfer.xlsx',sheet_name = '2014', skiprows=6)

    df = clean_council_housing(
        council_housing_2023,
        council_housing_2022,
        council_housing_2021,
        council_housing_2020,
        council_housing_2019,
        council_housing_2018,
        council_housing_2017,
        council_housing_2016,
        council_housing_2015,
        council_housing_2014

        )
    df.to_csv('data/processed/council_housing_cleaned.csv', index=False)

    print("✅ Cleaned dataset saved to: data/processed/council_housing_cleaned.csv")
