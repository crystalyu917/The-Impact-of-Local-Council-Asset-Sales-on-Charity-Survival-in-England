import pandas as pd

def clean_charity_main(file_path: str) -> pd.DataFrame:
    """
    Cleans the main charity register and returns a sorted dataset with status and postcode.
    """
    # Load data
    charity = pd.read_csv(file_path, low_memory=False)
    company_house = pd.read_csv('data/raw/companyHouseData2025.csv', low_memory=False)
    charity_web = pd.read_csv('data/raw/registeredCharityDataFromWeb.csv', low_memory=False)
    postcodes = pd.read_csv('data/raw/match_postcode_ONSPD2025.csv', low_memory=False)
    local_authority = pd.read_csv('data/raw/local_authority_names_and_codes_ONSPD2023.csv', low_memory=False)

    # Clean and process the charity register
    charity['registered_charity_number'] = charity['registered_charity_number'].astype(str).str.strip().str.zfill(6)
    charity['date_of_removal'] = pd.to_datetime(charity['date_of_removal'], errors='coerce')
    charity['charity_status'] = charity['date_of_removal'].apply(lambda x: 'active' if pd.isna(x) else 'inactive')
    charity['charity_company_registration_number'] = charity['charity_company_registration_number'].notna().astype(int)

    # Sort the charity register
    charity_sorted = charity.sort_values(
        by=['registered_charity_number', 'charity_status', 'charity_company_registration_number', 'date_of_removal'],
        ascending=[True, True, False, False]  # active first, has company number first, latest removal first
    )

    # Drop duplicates based on registered charity number
    charity_sorted = charity_sorted.drop_duplicates(subset='registered_charity_number', keep='first')

    
    # merge with company house data
    charity_sorted['charity_company_registration_number'] = charity_sorted['charity_company_registration_number'].astype(str).str.strip().str
    company_house = company_house.rename(columns={' CompanyNumber': 'CompanyNumber'})
    company_house['CompanyNumber'] = company_house['CompanyNumber'].astype(str).str.strip().str

    dataset = pd.merge(
    charity_sorted,
    company_house[['CompanyNumber', 'CompanyName', 'CompanyStatus', 'RegAddress.PostTown', 'RegAddress.PostCode', 'CompanyCategory', 'DissolutionDate']],
    left_on='charity_company_registration_number',
    right_on='CompanyNumber',
    how='left'
    )

    # merge with charity web data
    charity_web['charityNumber'] = charity_web['charityNumber'].astype(str).str.strip().str.zfill(6)
    charity_web = charity_web.rename(columns={'name': 'charity_name'})
    charity_web = charity_web.rename(columns={'charityNumber': 'registered_charity_number'})
    df = pd.merge(
    dataset,
    charity_web[['registered_charity_number', 'charity_name', 'companyNumber', 'postalCode', 'latestIncome', 'latestIncomeDate']],
    left_on=['registered_charity_number', 'charity_name'],
    right_on=['registered_charity_number', 'charity_name'],
    how='left'
    )
    

    # Clean up the dataset
    df.drop(columns='CompanyNumber', inplace=True)
    df.drop(columns='CompanyName', inplace=True)
    
    # use all the data - missing values in RegAddress.PostCode, postalCode, charity_contact_postcode
    df['postcode'] = (
    df['RegAddress.PostCode']
    .fillna(df['postalCode'])
    .fillna(df['charity_contact_postcode'])
    )

    #reorganise columns
    cols_to_front = ['registered_charity_number', 'charity_name', 'postcode', 'charity_status']
    other_cols = [col for col in df.columns if col not in cols_to_front]
    df = df[cols_to_front + other_cols]

    # Clean the postcode
    df['postcode'] = df['postcode'].astype(str).str.strip().str.upper()

    # Match postcodes to local authority names
    postcode_and_la = pd.merge(
    postcodes[['oslaua', 'pcds']],
    local_authority[['LAD23CD', 'LAD23NM']],
    left_on='oslaua',
    right_on='LAD23CD',
    how='left'
    )
    postcode_and_la = postcode_and_la.rename(columns={'pcds': 'postcode', 'LAD23NM': 'local_authority_name'})
    postcode_and_la = postcode_and_la.drop(columns=['LAD23CD', 'oslaua'])

    df['local_authority'] = df['postcode'].str.strip().str.upper().map(
    postcode_and_la.set_index('postcode')['local_authority_name']
    )

    return df