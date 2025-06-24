import pandas as pd
import numpy as np

def clean_charity_main(
    charity: pd.DataFrame,
    company_house: pd.DataFrame,
    charity_web: pd.DataFrame,
    postcodes: pd.DataFrame,
    local_authority: pd.DataFrame
) -> pd.DataFrame:
    """
    Cleans the main charity register and returns a sorted dataset with status,
    postcode, local authority, and size classification.
    """

    # Clean and process the charity register
    charity['registered_charity_number'] = charity['registered_charity_number'].astype(str).str.strip()
    charity['date_of_removal'] = pd.to_datetime(charity['date_of_removal'], errors='coerce')
    charity['charity_status'] = charity['date_of_removal'].apply(lambda x: 'active' if pd.isna(x) else 'inactive')
    charity['charity_company_registration_number'] = charity['charity_company_registration_number'].astype(str).str.strip()
    charity['has_company_number'] = charity['charity_company_registration_number'].ne("").astype(int)

    charity_sorted = charity.sort_values(
        by=['registered_charity_number', 'charity_status', 'has_company_number', 'date_of_removal'],
        ascending=[True, True, False, False]
    )

    charity_sorted = charity_sorted.drop_duplicates(subset='registered_charity_number', keep='first')

    # Merge with company house data
    company_house = company_house.rename(columns={' CompanyNumber': 'CompanyNumber'})
    company_house['CompanyNumber'] = company_house['CompanyNumber'].astype(str).str.strip()
    dataset = pd.merge(
        charity_sorted,
        company_house[['CompanyNumber', 'CompanyStatus', 'RegAddress.PostTown', 'RegAddress.PostCode', 'CompanyCategory', 'DissolutionDate']],
        left_on='charity_company_registration_number',
        right_on='CompanyNumber',
        how='left'
    )

    # Merge with charity web data
    charity_web['charityNumber'] = charity_web['charityNumber'].astype(str).str.strip()
    charity_web = charity_web.rename(columns={'name': 'charity_name', 'charityNumber': 'registered_charity_number'})
    df = pd.merge(
        dataset,
        charity_web[['registered_charity_number', 'charity_name', 'companyNumber', 'postalCode', 'latestIncome', 'latestIncomeDate']],
        on=['registered_charity_number', 'charity_name'],
        how='left'
    )

    df.drop(columns=['CompanyNumber', 'CompanyCategory'], inplace=True)

    # Create postcode field from multiple sources
    df['postcode'] = (
        df['RegAddress.PostCode']
        .fillna(df['postalCode'])
        .fillna(df['charity_contact_postcode'])
    )

    # Reorganise columns
    cols_to_front = ['registered_charity_number', 'charity_name', 'postcode', 'charity_status']
    df = df[cols_to_front + [col for col in df.columns if col not in cols_to_front]]

    # Clean postcode
    df['postcode'] = df['postcode'].astype(str).str.strip().str.upper()

    # Map postcode to local authority
    postcode_and_la = pd.merge(
        postcodes[['oslaua', 'pcds']],
        local_authority[['LAD23CD', 'LAD23NM']],
        left_on='oslaua',
        right_on='LAD23CD',
        how='left'
    )
    postcode_and_la = postcode_and_la.rename(columns={'pcds': 'postcode', 'LAD23NM': 'local_authority_name'})
    df['local_authority'] = df['postcode'].map(postcode_and_la.set_index('postcode')['local_authority_name'])

    # Classify charity size
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
    columns_to_drop = [
        'latestIncome',
        'latestIncomeDate',
        'has_company_number',
        'RegAddress.PostTown',
        'CompanyStatus',
        'date_of_extract',
        'date_cio_dissolution_notice',
        'cio_is_dissolved',
        'charity_is_cio',
        'charity_is_cdf_or_cif',
        'charity_previously_excepted',
        'charity_in_administration',
        'charity_activities',
        'postalCode',
        'RegAddress.PostCode',
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
        'charity_contact_postcode',
        'charity_contact_phone',
        'charity_contact_email',
        'charity_contact_web',
        'DissolutionDate',
        'charity_registration_status',
        'charity_company_registration_number',
        'charity_insolvent'
    ]

    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    return df