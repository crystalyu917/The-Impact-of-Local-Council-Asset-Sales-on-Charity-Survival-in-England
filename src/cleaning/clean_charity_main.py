import pandas as pd
import numpy as np

CATEGORY_MAPPING = {
    # Charities primarily providing financial or material aid
    'Grantmaking_And_Financial_Support': [
        'classification_makes_grants_to_individuals',
        'classification_makes_grants_to_organisations',
        'classification_provides_other_finance'
    ],

    # Charities focused on accommodation, land, or physical spaces
    'Housing_And_Infrastructure': [
        'classification_accommodation/housing',
        'classification_provides_buildings/facilities/open_space'
    ],

    # Schools, research institutions, training
    'Education_And_Research': [
        'classification_education/training',
        'classification_sponsors_or_undertakes_research'
    ],

    # Youth development, sports
    'Children_And_Youth': [
        'classification_children/young_people',
        'classification_amateur_sport'
    ],

    # Health-related causes and support for disabilities
    'Health_And_Disability': [
        'classification_the_advancement_of_health_or_saving_of_lives',
        'classification_disability',
        'classification_people_with_disabilities'
    ],

    # Rights, advocacy, and equalities work
    'Advocacy_And_Human_Rights': [
        'classification_human_rights/religious_or_racial_harmony/equality_or_diversity',
        'classification_provides_advocacy/advice/information',
        'classification_people_of_a_particular_ethnic_or_racial_origin'
    ],

    # Faith-based or religious missions
    'Religious_Activities': [
        'classification_religious_activities'
    ],

    # Environmental and animal welfare work
    'Environment_And_Animals': [
        'classification_environment/conservation/heritage',
        'classification_animals'
    ],

    # General welfare, community improvement, poverty relief
    'Community_And_Social_Welfare': [
        'classification_economic/community_development/employment',
        'classification_general_charitable_purposes',
        'classification_the_prevention_or_relief_of_poverty',
        'classification_provides_services',
        'classification_other_charitable_activities',
        'classification_other_charitable_purposes'
    ],

    # Charities supporting the sector or other organisations
    'Charity_Sector_Support': [
        'classification_acts_as_an_umbrella_or_resource_body',
        'classification_other_charities_or_voluntary_bodies',
        'classification_provides_human_resources'
    ],

    # Overseas development and aid
    'International_And_Humanitarian': [
        'classification_overseas_aid/famine_relief'
    ],

    # Services for older people
    'Elderly_Support': [
        'classification_elderly/old_people'
    ],

    # Broad beneficiaries or undefined groups
    'General_Public_And_Misc': [
        'classification_the_general_public/mankind',
        'classification_other_defined_groups'
    ],

    # Arts, culture, recreation and leisure
    'Arts_And_Recreation': [
        'classification_arts/culture/heritage/science',
        'classification_recreation'
    ],

    # Armed forces, emergency services efficiency
    'Military_And_Civil_Efficiency': [
        'classification_armed_forces/emergency_service_efficiency'
    ]
}

def apply_category_mapping(
        value: str
    ) -> str:
    
    value = str(value).replace(' ', '_').replace('-', '_').lower()
    value = f"classification_{value}"
    for key in CATEGORY_MAPPING.keys():
        if value in CATEGORY_MAPPING[key]:
            return key
    else:
        return 'Other'

def base_cleaning(
        charity: pd.DataFrame
    )-> pd.DataFrame:
    """
    Conduct base cleaning for charity data.
    """
    # Enforce typing
    type_map = {
        'registered_charity_number': str,
        'date_of_removal': 'datetime64[ns]',
        'charity_company_registration_number': str,
        'charity_status': str
    }
    for col, dtype in type_map.items():
        if col in charity.columns:
            if dtype == 'datetime64[ns]':
                charity[col] = pd.to_datetime(charity[col], errors='coerce')
            elif dtype == str:
                charity[col] = charity[col].astype(str).str.strip()
            elif dtype == int:
                string_cols = charity[col].astype(str).str.strip()
                charity[col] = string_cols.astype(int)

    # Boolean indicator for company number
    charity['has_company_number'] = (
        charity['charity_company_registration_number'].ne("").astype(int)
        )
    
    # Charity status for filtering
    charity['charity_status'] = charity['date_of_removal'].apply(
        lambda x: 'active' if pd.isna(x) else 'inactive'
        )
    # Drop duplicates via charity number keep most recent active record
    charity_sorted = charity.sort_values(
        by=[
            'registered_charity_number', 
            'charity_status', 
            'has_company_number', 
            'date_of_removal'
            ],
        ascending=[True, True, False, False]
    ).drop_duplicates(subset='registered_charity_number', keep='first')

    return charity_sorted

def process_company_house_inplace(company_house: pd.DataFrame):
    """
    Process Company House data to ensure correct column names & types.
    """
    company_house.rename(
        columns={
            ' CompanyNumber': 'CompanyNumber'
        },
        inplace=True
    )
    
    # Ensure CompanyNumber is string and stripped of whitespace
    company_house['CompanyNumber'] = (
        company_house['CompanyNumber']
        .astype(str)
        .str.strip()
    )

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
    charity_sorted = base_cleaning(charity)
    process_company_house_inplace(company_house)

    # Merge with company house data
    dataset = pd.merge(
        charity_sorted,
        company_house[['CompanyNumber', 'CompanyStatus', 'RegAddress.PostCode']],
        left_on='charity_company_registration_number',
        right_on='CompanyNumber',
        how='left'
    )
    dataset.drop(columns=['CompanyNumber'], inplace=True)

    # --- Step 3: Merge with Charity Web data ---
    charity_web['charityNumber'] = charity_web['charityNumber'].astype(str).str.strip()
    charity_web = charity_web.rename(columns={'name': 'charity_name', 'charityNumber': 'registered_charity_number'})
    df = pd.merge(
        dataset,
        charity_web[['registered_charity_number', 'charity_name', 'postalCode', 'latestIncome']],
        on=['registered_charity_number', 'charity_name'],
        how='left'
    )
   

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

    # Define function to get financial year
    def get_financial_year(date):
        if pd.isna(date):
            return np.nan
        return date.year if date.month >= 4 else date.year - 1

    # --- ensure dates are in datetime ---
    df['date_of_registration'] = pd.to_datetime(df['date_of_registration'], errors='coerce')
    df['date_of_removal'] = pd.to_datetime(df['date_of_removal'], errors='coerce')

    df['registration_year'] = df['date_of_registration'].dt.to_period('Y')
    df['removal_year'] = df['date_of_removal'].dt.to_period('Y')

    df['registration_month'] = df['date_of_registration'].dt.to_period('M')
    df['removal_month'] = df['date_of_removal'].dt.to_period('M')

    df['registration_fy'] = df['date_of_registration'].apply(get_financial_year)
    df['removal_fy'] = df['date_of_removal'].apply(get_financial_year)

    df['classification_description'] = df['classification_description'].apply(apply_category_mapping)
    
    # Drop duplicates incase charity match multiple sub-cat inside the same category
    df.drop_duplicates(
        subset =['registered_charity_number', 'classification_description'], inplace=True
        )

    # Step 1: Drop rows with missing classification
    classification_df = df[['registered_charity_number', 'classification_description']].dropna()

    # Step 2: Create binary indicator (1) for each classification
    classification_df['value'] = 1

    # Step 3: Pivot to wide format with binary columns
    classification_dummies = classification_df.pivot_table(
        index='registered_charity_number',
        columns='classification_description',
        values='value',
        aggfunc='max',
        fill_value=0
    )

    

    # Step 5: Reset index and merge with original dataset
    classification_dummies = classification_dummies.reset_index()
    df = df.drop_duplicates(subset='registered_charity_number')  # ensure one row per charity
    df = df.merge(classification_dummies, on='registered_charity_number', how='left')

    # Identify classification dummy columns (typically start with 'classification_')
    category_cols = [col for col in df.columns if col.startswith('classification_')]

    # Fill NaNs with 0 in those columns only
    df[category_cols] = df[category_cols].fillna(0)

    return df
