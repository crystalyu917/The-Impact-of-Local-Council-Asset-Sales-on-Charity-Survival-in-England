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

    # Step 4: Optional – rename columns for consistency (e.g., no spaces or special chars)
    classification_dummies.columns = [
        f"classification_{str(col).replace(' ', '_').replace('-', '_').lower()}"
        for col in classification_dummies.columns
    ]

    # Step 5: Reset index and merge with original dataset
    classification_dummies = classification_dummies.reset_index()
    df = df.drop_duplicates(subset='registered_charity_number')  # ensure one row per charity
    df = df.merge(classification_dummies, on='registered_charity_number', how='left')

    # Identify classification dummy columns (typically start with 'classification_')
    category_cols = [col for col in df.columns if col.startswith('classification_')]

    # Fill NaNs with 0 in those columns only
    df[category_cols] = df[category_cols].fillna(0)

    category_map = {
    'classification_makes_grants_to_individuals': 'Grants_Related',
    'classification_makes_grants_to_organisations': 'Grants_Related',
    'classification_accommodation/housing': 'Housing_Infrastructure',
    'classification_provides_buildings/facilities/open_space': 'Housing_Infrastructure',
    'classification_education/training': 'Education_Research',
    'classification_sponsors_or_undertakes_research': 'Education_Research',
    'classification_children/young_people': 'Children_Youth',
    'classification_amateur_sport': 'Children_Youth',
    'classification_the_advancement_of_health_or_saving_of_lives': 'Health_Disability',
    'classification_disability': 'Health_Disability',
    'classification_people_with_disabilities': 'Health_Disability',
    'classification_human_rights/religious_or_racial_harmony/equality_or_diversity': 'Human_Rights_Advocacy',
    'classification_provides_advocacy/advice/information': 'Human_Rights_Advocacy',
    'classification_people_of_a_particular_ethnic_or_racial_origin': 'Human_Rights_Advocacy',
    'classification_religious_activities': 'Religion_Faith',
    'classification_acts_as_an_umbrella_or_resource_body': 'Religion_Faith',
    'classification_environment/conservation/heritage': 'Environment_Animals',
    'classification_animals': 'Environment_Animals',
    'classification_economic/community_development/employment': 'Economic_Social_Development',
    'classification_general_charitable_purposes': 'Economic_Social_Development',
    'classification_provides_services': 'Economic_Social_Development',
    'classification_provides_human_resources': 'Economic_Social_Development',
    'classification_provides_other_finance': 'Economic_Social_Development',
    'classification_other_charitable_purposes': 'Economic_Social_Development',
    'classification_other_charities_or_voluntary_bodies': 'Economic_Social_Development',
    'classification_other_charitable_activities': 'Economic_Social_Development',
    'classification_the_prevention_or_relief_of_poverty': 'Economic_Social_Development',
    'classification_overseas_aid/famine_relief': 'Overseas_Famine_Relief',
    'classification_the_general_public/mankind': 'Other_Miscellaneous',
    'classification_other_defined_groups': 'Other_Miscellaneous',
    'classification_recreation': 'Other_Miscellaneous',
    'classification_elderly/old_people': 'Other_Miscellaneous',
    'classification_armed_forces/emergency_service_efficiency': 'Other_Miscellaneous',
    'classification_arts/culture/heritage/science': 'Other_Miscellaneous',
    }
    # Invert mapping: dummy_col -> group
    dummy_to_group = {col: group for col, group in category_map.items()}

    # Prepare a DataFrame to hold new dummy columns
    group_dummies = pd.DataFrame(0, index=df.index, columns=sorted(set(dummy_to_group.values())))

    # Assign each charity to the first matching group only (no double count)
    for idx, row in df.iterrows():
        for col, group in dummy_to_group.items():
            if col in df.columns and row[col] == 1:
                group_dummies.at[idx, group] = 1
                break  # stop after first match
    df = pd.concat([df, group_dummies], axis=1)
    
    category_drop = {
        'classification_makes_grants_to_individuals',
        'classification_makes_grants_to_organisations',
        'classification_accommodation/housing',
        'classification_provides_buildings/facilities/open_space',
        'classification_education/training',
        'classification_sponsors_or_undertakes_research',
        'classification_children/young_people',
        'classification_amateur_sport',
        'classification_the_advancement_of_health_or_saving_of_lives',
        'classification_disability',
        'classification_people_with_disabilities',
        'classification_human_rights/religious_or_racial_harmony/equality_or_diversity',
        'classification_provides_advocacy/advice/information',
        'classification_people_of_a_particular_ethnic_or_racial_origin',
        'classification_religious_activities',
        'classification_acts_as_an_umbrella_or_resource_body',
        'classification_environment/conservation/heritage',
        'classification_animals',
        'classification_economic/community_development/employment',
        'classification_general_charitable_purposes',
        'classification_provides_services',
        'classification_provides_human_resources',
        'classification_provides_other_finance',
        'classification_other_charitable_purposes',
        'classification_other_charities_or_voluntary_bodies',
        'classification_other_charitable_activities',
        'classification_the_prevention_or_relief_of_poverty',
        'classification_overseas_aid/famine_relief',
        'classification_the_general_public/mankind',
        'classification_other_defined_groups',
        'classification_recreation',
        'classification_elderly/old_people',
        'classification_armed_forces/emergency_service_efficiency',
        'classification_arts/culture/heritage/science'
    }
    df = df.drop(columns=category_drop, errors='ignore')

    return df
