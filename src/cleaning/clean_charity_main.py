import pandas as pd
import numpy as np

def clean_charity_main(
    charity: pd.DataFrame,
    company_house: pd.DataFrame,
    charity_web: pd.DataFrame,
    postcodes: pd.DataFrame,
    local_authority: pd.DataFrame,
    category: pd.DataFrame,
) -> pd.DataFrame:
    '''
    Cleans the main charity register and returns a sorted dataset with key information such as charity registration and deregistration date,
    status, local authority, and size classification.
    '''
    # --- Step 1: Charity base cleaning ---
    charity['registered_charity_number'] = charity['registered_charity_number'].astype(str).str.strip()
    charity['date_of_removal'] = pd.to_datetime(charity['date_of_removal'], errors='coerce')
    charity['charity_company_registration_number'] = charity['charity_company_registration_number'].astype(str).str.strip()
    charity['has_company_number'] = charity['charity_company_registration_number'].ne("").astype(int)
    charity['charity_status'] = charity['date_of_removal'].apply(lambda x: 'active' if pd.isna(x) else 'inactive')

    charity_sorted = charity.sort_values(
        by=['registered_charity_number', 'charity_status', 'has_company_number', 'date_of_removal'],
        ascending=[True, True, False, False]
    ).drop_duplicates(subset='registered_charity_number', keep='first')

    # --- Step 2: Merge with Company House data ---
    company_house = company_house.rename(columns={' CompanyNumber': 'CompanyNumber'})
    company_house['CompanyNumber'] = company_house['CompanyNumber'].astype(str).str.strip()
    dataset = pd.merge(
        charity_sorted,
        company_house[['CompanyNumber', 'CompanyStatus', 'RegAddress.PostCode']],
        left_on='charity_company_registration_number',
        right_on='CompanyNumber',
        how='left'
    )

    # --- Step 3: Merge with Charity Web data ---
    charity_web['charityNumber'] = charity_web['charityNumber'].astype(str).str.strip()
    charity_web = charity_web.rename(columns={'name': 'charity_name', 'charityNumber': 'registered_charity_number'})
    df = pd.merge(
        dataset,
        charity_web[['registered_charity_number', 'charity_name', 'companyNumber', 'postalCode', 'latestIncome']],
        on=['registered_charity_number', 'charity_name'],
        how='left'
    )
    df.drop(columns=['CompanyNumber'], inplace=True)

    # --- Step 4: Postcode and local authority mapping ---
    df['postcode'] = (
        df['RegAddress.PostCode']
        .fillna(df['postalCode'])
        .fillna(df['charity_contact_postcode'])
    ).astype(str).str.strip().str.upper()

    postcode_and_la = pd.merge(
        postcodes[['oslaua', 'pcds']],
        local_authority[['LAD23CD', 'LAD23NM']],
        left_on='oslaua',
        right_on='LAD23CD',
        how='left'
    ).rename(columns={'pcds': 'postcode', 'LAD23NM': 'local_authority_name'})

    df['local_authority'] = df['postcode'].map(postcode_and_la.set_index('postcode')['local_authority_name'])

    # --- Step 5: Size classification ---
    def classify_size_combined(row):
        income = row['latest_income']
        if pd.isna(income):
            income = row['latestIncome']
        if pd.isna(income):
            return np.nan
        elif income < 25000:
            return 'Small'
        elif income <= 1_000_000:
            return 'Medium'
        else:
            return 'Large'

    df['size_category'] = df.apply(classify_size_combined, axis=1)

    # --- Step 6: Merge with Category (Classification) ---
    df['registered_charity_number'] = df['registered_charity_number'].astype(str).str.strip().str.zfill(6)
    category['registered_charity_number'] = category['registered_charity_number'].astype(str).str.strip().str.zfill(6)

    df = pd.merge(df, category, on='registered_charity_number', how='left')

    # --- Step 7: Drop unnecessary columns ---
    columns_to_drop = [
        'RegAddress.PostCode',
        'postalCode',
        'charity_contact_postcode',
        'latestIncome',
        'has_company_number',
        'CompanyStatus',
        'date_of_extract',
        'date_cio_dissolution_notice',
        'cio_is_dissolved',
        'charity_is_cio',
        'charity_is_cdf_or_cif',
        'charity_previously_excepted',
        'charity_in_administration',
        'charity_gift_aid',
        'charity_reporting_status',
        'latest_acc_fin_period_start_date',
        'latest_acc_fin_period_end_date',
        'latest_expenditure',
        'charity_contact_address1',
        'charity_contact_address2',
        'charity_contact_address3',
        'charity_contact_address4',
        'charity_contact_address5',
        'charity_contact_phone',
        'charity_contact_email',
        'charity_contact_web',
        'charity_registration_status',
        'charity_company_registration_number',
        'charity_insolvent',
        'classification_code',
        'classification_type',
        'linked_charity_number_y',
        'organisation_number_y',
        'date_of_extract_y',
        'linked_charity_number_x',
        'organisation_number_x',
        'date_of_extract_x'
    ]
    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # --- Step 8: Final column order ---
    cols_to_front = ['registered_charity_number', 'charity_name', 'postcode', 'charity_status']
    df = df[cols_to_front + [col for col in df.columns if col not in cols_to_front]]

    return df
