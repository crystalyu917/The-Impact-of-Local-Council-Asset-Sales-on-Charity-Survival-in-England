import pandas as pd
import re
from fuzzywuzzy import process

def clean_la_assets(la_files, la_name_file):
    # Load and concatenate all LA asset files
    la_dfs = [pd.read_excel(file) for file in la_files]
    la = pd.concat(la_dfs, ignore_index=True)

    la_names = pd.read_csv(la_name_file)

    # Summarise asset data
    asset_summary = la.groupby('LocalAuthority').agg(
        total_assets=('OBJECTID', 'count'),
        total_land_area=('LandAreaHA', 'sum'),
        avg_land_area=('LandAreaHA', 'mean'),
        land_only_assets=('HoldingTypeDescription', lambda x: (x == 'Land Only').sum()),
        buildings_only_assets=('HoldingTypeDescription', lambda x: (x == 'Buildings Only').sum()),
        land_building_assets=('HoldingTypeDescription', lambda x: (x == 'Land/Buildings').sum()),
        percent_freehold=('TenureTypeDescription', lambda x: (x == 'Freehold/Feuhold/Fee Simple').mean()),
        registered_titles=('Titles', lambda x: x.str.contains('Registered', na=False).sum()),
    ).reset_index()

    
    asset_summary = asset_summary.rename(columns={'LocalAuthority': 'local_authority'})

    # Clean the asset summary council names
    asset_summary['simplified_name'] = (
        asset_summary['local_authority']
        .str.extract(r'^(.*?)\s*\(')[0]  # remove codes in brackets
        .str.replace(
            r'\b(DISTRICT|BOROUGH|CITY|LONDON BOROUGH|METROPOLITAN BOROUGH|COUNCIL|UNITARY|COUNTY|OF)\b',
            '',
            flags=re.IGNORECASE,
            regex=True
        )
        .str.strip()
        .str.title()
    )

    # Manual replacement for abolished councils
    abolished_to_new = {
        'Allerdale': 'Cumberland',
        'Carlisle': 'Cumberland',
        'Copeland': 'Cumberland',
        'Eden': 'Westmorland and Furness',
        'South Lakeland': 'Westmorland and Furness',
        'Barrow-In-Furness': 'Westmorland and Furness',
        'Craven': 'North Yorkshire',
        'Harrogate': 'North Yorkshire',
        'Hambleton': 'North Yorkshire',
        'Richmondshire': 'North Yorkshire',
        'Ryedale': 'North Yorkshire',
        'Scarborough': 'North Yorkshire',
        'Selby': 'North Yorkshire',
        'Mendip': 'Somerset',
        'Sedgemoor': 'Somerset',
        'South Somerset': 'Somerset',
        'Somerset West And Taunton': 'Somerset',
        'Corby': 'North Northamptonshire',
        'East Northamptonshire': 'North Northamptonshire',
        'Kettering': 'North Northamptonshire',
        'Wellingborough': 'North Northamptonshire',
        'Daventry': 'West Northamptonshire',
        'Northampton': 'West Northamptonshire',
        'South Northamptonshire': 'West Northamptonshire',
    }
    asset_summary['simplified_name'] = asset_summary['simplified_name'].replace(abolished_to_new)


    # Ensure string values
    asset_summary['simplified_name'] = asset_summary['simplified_name'].fillna('').astype(str)
    official_la_names = la_names['LAD23NM'].dropna().astype(str).unique()

    # Step 3: Fuzzy match to official English local authority names
    def fuzzy_match(name, choices):
        if not name or name.strip() == "":
            return pd.Series([None, 0])
        match, score = process.extractOne(name, choices)
        return pd.Series([match, score])

    asset_summary[['matched_la', 'match_score']] = asset_summary['simplified_name'].apply(
        fuzzy_match,
        choices=official_la_names
    )

    # Show the 10 lowest fuzzy match scores for inspection
    lowest_scores = asset_summary.nsmallest(10, 'match_score')[['simplified_name', 'matched_la', 'match_score']]

    manual_la_fix = {
        'Shepway': 'Folkestone and Hythe',
        'North Northants': 'North Northamptonshire',
        'West Northants': 'West Northamptonshire',
    }

    asset_summary['matched_la'] = asset_summary.apply(
        lambda row: manual_la_fix[row['simplified_name']] if row['simplified_name'] in manual_la_fix else row['matched_la'],
        axis=1
    )

    # Reorder columns to make 'matched_la' first
    cols = ['matched_la'] + [col for col in asset_summary.columns if col != 'matched_la']
    asset_summary = asset_summary[cols]

    asset_summary = asset_summary.drop(columns=['match_score', 'simplified_name', 'local_authority'])
    asset_summary = asset_summary.rename(columns={'matched_la': 'local_authority'})

    return asset_summary