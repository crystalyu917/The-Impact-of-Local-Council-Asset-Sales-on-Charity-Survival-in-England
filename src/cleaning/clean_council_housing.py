import pandas as pd

def clean_council_housing(
    council_housing_2023: pd.DataFrame,
    council_housing_2022: pd.DataFrame,
    council_housing_2021: pd.DataFrame,
    council_housing_2020: pd.DataFrame,
    council_housing_2019: pd.DataFrame,
    council_housing_2018: pd.DataFrame,
    council_housing_2017: pd.DataFrame,
    council_housing_2016: pd.DataFrame,
    council_housing_2015: pd.DataFrame,
    council_housing_2014: pd.DataFrame
) -> pd.DataFrame:
    """
    Cleans and merges LAHS sales and transfers data from 2014 to 2023.
    Keeps only selected columns and standardises naming.
    """

    rename_dict = {
        'b2aa': 'Right_to_Buy_total_number_of_dwellings',
        'b2ba': 'Social_Homebuy_number_of_dwellings',
        'b2ca': 'Other_sales_to_sitting_tenants_number_of_dwellings',
        'b2da': 'Other_sales_number_of_dwellings',
        'b2ea': 'Transfers_to_PRPs',
        'b4aa': 'Sales_of_Shared_Ownership_number_of_dwellings'
    }

    dfs = {
        2023: council_housing_2023,
        2022: council_housing_2022,
        2021: council_housing_2021,
        2020: council_housing_2020,
        2019: council_housing_2019,
        2018: council_housing_2018,
        2017: council_housing_2017,
        2016: council_housing_2016,
        2015: council_housing_2015,
        2014: council_housing_2014
    }

    cleaned_dfs = []
    
    for year, df in dfs.items():
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['Local authority'])
        df = df.rename(columns=rename_dict)
        keep_cols = ['Local authority'] + list(rename_dict.values())
        df = df[[col for col in df.columns if col in keep_cols]]
        df['Financial_Year'] = year

        cleaned_dfs.append(df)

    combined = pd.concat(cleaned_dfs, ignore_index=True)
    return combined
