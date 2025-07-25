# clean_receipt.py

import pandas as pd
import numpy as np
import itertools

YEAR_SKIP_MAPPING = {
    "2014": 0, "2015": 0, "2016": 2, "2017": 3, "2018": 3,
    "2019": 4, "2020": 4, "2021": 4, "2022": 4, "2023": 4,
}

merge_columns = {
    "community safety": ["community safety", "community safety (cctv)"],
    'agricultural & fisheries services':['agriculture & fisheries'],
    'all services total':['total all services','all services'],
    'early years & primary schools':['pre-primary & primary education'],
    'parking':['parking of vehicles'],
    'ports & piers':['local authority ports & piers'],
    'special schools & alternative provision':['special education'],
    'secondary schools':['secondary education'],
    'total industrial & commercial trading':['industrial & commercial trading'],
    'total environmental & regulatory services':['total environmental services','regulatory services (environmental health)'],
    'tolled roads, bridges, tunnels,ferries & public transport companies':['tolled road bridges, tunnels, ferries, public transport companies','tolled road bridges, tunnels, ferries & public transport companies'],
    'public transport (bus)':['public passenger transport - bus'],
    'public transport (rail & other)':['public passenger transport - rail & other'],
    'total housing':['housing'],
    'total police':['police'],
    'total social care':['social services','social care'],
    'total public health':['public health'],
    'roads, street lighting & road safety':['roads, street lights & safety'],
    'total fire & rescue services':['fire & rescue services'],
    'total central services':['central services (including court services)'],
    'street cleaning (not chargeable to highways)':['street cleaning not chargeable to highways'],
    'total planning & development':['total planning & development services','planning & development services'],
    'total trading services':['total trading','trading'],
    'total education':['education'],
    'total highways & transport':['total transport','highways & transport'],
    'total culture & related services':['culture & heritage']

    #'commercial housing',
    #'energy generation & supply',
    #'finance & insurance activity',
    #'hospitality & catering',
    #'lgf code',
    #'ons code',
    #'other commercial activity',
    #'other real estate activities',
    #'post-16 provision & other education',
    #'subclass',
    #'total digital infrastructure',
    #'water supply, sewerage & remediation'
}

# Combined mapping: new_name → list of old names
unified_map = {
    'buckinghamshire': ['aylesbury vale', 'chiltern', 'south bucks', 'wycombe','south buckinghamshire'],
    'dorset': ['weymouth and portland', 'west dorset', 'north dorset', 'east dorset', 'purbeck', 'christchurch'],
    'somerset': ['taunton deane', 'west somerset', 'mendip', 'sedgemoor', 'south somerset', 'somerset council','somerset west and taunton'],
    'cumberland': ['allerdale', 'carlisle', 'copeland', 'cumberland council'],
    'westmorland and furness': ['barrow in furness', 'barrow-in-furness', 'eden', 'south lakeland'],
    'north yorkshire': ['craven', 'hambleton', 'harrogate', 'richmondshire', 'ryedale', 'scarborough', 'selby', 'north yorkshire council'],
    'bournemouth christchurch and poole': ['bournemouth', 'christchurch', 'poole'],
    'west suffolk': ['forest heath', 'st edmundsbury'],
    'east suffolk': ['suffolk coastal', 'waveney'],
    'bath and north east somerset': ['bath and ne somerset'],
    'southend-on-sea': ['southend on sea'],
    'leicester': ['leicester city'],
    'medway': ['medway towns'],
    'derby': ['derby city'],
    'folkestone and hythe': ['shepway'],
    'county durham': ['durham'],
    "king's lynn and west norfolk": ['kings lynn and west norfolk'],
    'north northamptonshire': ['wellingborough', 'east northamptonshire', 'kettering', 'corby'],
    'west northamptonshire': ['northampton', 'south northamptonshire', 'daventry'],
}

# old_name → new_name (lowercase)
flat_lookup = {
    old.lower(): new.lower()
    for new, olds in unified_map.items()
    for old in olds
}

# List of known devolved nation council names to exclude
non_england_keywords = [
    'aberdeen', 'aberdeenshire', 'angus', 'antrim', 'ards', 'argyll', 'armagh', 'belfast', 'blaenau', 'bridgend',
    'caerphilly', 'cardiff', 'carmarthenshire', 'causeway', 'ceredigion', 'conwy', 'denbighshire', 'derry',
    'dumfries', 'dundee', 'east ayrshire', 'east dunbartonshire', 'east lothian', 'east renfrewshire', 'falkirk',
    'fermanagh', 'fife', 'flintshire', 'glasgow', 'gwynedd', 'highland', 'inverclyde', 'isle of man',
    'isle of anglesey', 'lisburn', 'merthyr', 'mid and east antrim', 'mid ulster', 'midlothian', 'monmouthshire',
    'moray', 'na h eileanan siar', 'neath', 'newport', 'newry', 'north ayrshire', 'north lanarkshire', 'orkney',
    'pembrokeshire', 'perth and kinross', 'powys', 'renfrewshire', 'rhondda', 'scottish borders', 'shetland',
    'south ayrshire', 'south lanarkshire', 'stirling', 'swansea', 'torfaen', 'vale of glamorgan', 'west dunbartonshire',
    'west lothian', 'wrexham','city of edinburgh','channel islands'
]

def clean_sheet(df, rename_from_col=3, header_row=1):
    renamed_mask = [not str(col).startswith("Unnamed:") for col in df.columns]
    cols_to_keep = list(range(rename_from_col + 1))
    for i in range(rename_from_col + 1, len(df.columns)):
        if renamed_mask[i]:
            cols_to_keep.append(i)
    for i in range(rename_from_col, len(df.columns)):
        if renamed_mask[i]:
            df.iloc[header_row, i] = df.columns[i]
    df.columns = df.iloc[header_row]
    df = df.drop(index=list(range(header_row + 1))).reset_index(drop=True)
    return df.iloc[:, cols_to_keep]

def rename_and_filter_disposal(df, start_col=5, keyword=": Disposal of tangible fixed assets"):
    cols_to_keep = list(range(start_col))
    new_columns = df.columns.tolist()
    for i in range(start_col, len(df.columns)):
        col = str(df.columns[i])
        if keyword in col:
            new_columns[i] = col.replace(keyword, "")
            cols_to_keep.append(i)
    df.columns = new_columns
    return df.iloc[:, cols_to_keep]

def basic_cleaning(df, index):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    if 'la name' in df.columns:
        df = df.rename(columns={'la name': 'local_authority'})
    if 'local_authority' in df.columns:
        df['local_authority'] = df['local_authority'].str.lower()
        df['local_authority'] = df['local_authority'].str.replace(r' \(ua\)|\\bua\\b| ua', '', regex=True).str.strip()
    first_col = df.columns[0]
    df = df[~df[first_col].isin([pd.NA, None, '[z]', 'la_lgf_code'])]
    df = df.dropna(subset=[first_col])
    if index == 0 and 'ecode' in df.columns:
        df = df.dropna(subset=['ecode'])
    elif index != 0 and 'ons code' in df.columns:
        df = df.dropna(subset=['ons code'])
    if 'class' in df.columns:
        df = df[~df['class'].isin(['O','SC'])]
    return df.reset_index(drop=True)

def merge_columns_func(dfs, merge_columns):
    for idx in range(len(dfs)):
        df = dfs[idx].copy()
        df.columns = [str(col).strip().lower().replace(" and ", " & ") for col in df.columns]
        for standard_col, aliases in merge_columns.items():
            present_cols = [col for col in aliases if col in df.columns]
            if present_cols:
                df.loc[:, standard_col] = df[present_cols].sum(axis=1, skipna=True)
                cols_to_drop = [col for col in present_cols if col != standard_col]
                df.drop(columns=cols_to_drop, inplace=True)
        dfs[idx] = df
    return dfs

def clean_local_authority(name, flat_lookup):
    if pd.isna(name):
        return name
    name = (str(name).lower().replace('&', 'and').replace('-', ' ').replace(',', '').replace('.', '')
            .replace(' city of', '').replace(' county of', '').strip())
    return flat_lookup.get(name, name)

def apply_local_authority_cleaning(dfs, dataset, flat_lookup):
    for i in range(len(dfs)):
        if 'local_authority' in dfs[i].columns:
            dfs[i]['local_authority'] = dfs[i]['local_authority'].apply(lambda x: clean_local_authority(x, flat_lookup))
    if 'local_authority' in dataset.columns:
        dataset['local_authority'] = dataset['local_authority'].apply(lambda x: clean_local_authority(x, flat_lookup))
    return dfs, dataset

def filter_non_england(dataset, non_england_keywords):
    dataset['local_authority_lower'] = dataset['local_authority'].str.lower()
    dataset = dataset[~dataset['local_authority_lower'].str.contains('|'.join(non_england_keywords), na=False)]
    return dataset.drop(columns=['local_authority_lower'])

def melt_disposal(dfs):
    long_frames = []
    years = list(range(2014, 2024))
    for i, df in enumerate(dfs):
        if df.empty or 'local_authority' not in df.columns:
            continue
        df['financial_year'] = years[i]
        long_df = df.melt(
            id_vars=["local_authority", "financial_year"],
            value_vars=[col for col in df.columns if col not in ["ecode", 'lgf code', 'ons code', "class", "subclass", "local_authority", "financial_year", 'certification complete']],
            var_name="category", value_name="value"
        )
        long_frames.append(long_df)
    return pd.concat(long_frames, ignore_index=True)

def create_complete_panel(disposal_long_df, dataset):
    removals = dataset.groupby(['local_authority', 'removal_fy', 'size_category']).size().reset_index(name='removals').rename(columns={'removal_fy': 'financial_year'})
    disposal_long_df = disposal_long_df[disposal_long_df['category'] == 'all services total']
    disposal_long_df = disposal_long_df.groupby(['local_authority', 'financial_year', 'category']).agg({'value': 'sum'}).reset_index()
    
    unique_years = disposal_long_df['financial_year'].unique()
    unique_authorities = disposal_long_df['local_authority'].unique()
    unique_size_categories = removals['size_category'].dropna().unique()
    all_combinations = list(itertools.product(unique_years, unique_authorities, unique_size_categories))
    complete_index = pd.DataFrame(all_combinations, columns=['financial_year', 'local_authority', 'size_category'])
    
    complete_disposal = pd.merge(complete_index, disposal_long_df, on=["financial_year", "local_authority"], how="left")
    panel = pd.merge(complete_disposal, removals, how="left", on=['local_authority', 'financial_year','size_category'] )
    
    panel['removals'] = panel['removals'].fillna(0).astype(int)
    panel = panel[(panel['financial_year'] >= 2015) & (panel['financial_year'] <= 2023)]
    panel['value'] = pd.to_numeric(panel['value'], errors='coerce')/1000
    panel['removals'] = panel['removals'].fillna(0).astype(int)
    panel['value'] = panel.groupby(['local_authority', 'financial_year'])['value'].transform('first')
    filtered_panel = panel.drop(columns=['category'], errors='ignore').sort_values(['local_authority', 'size_category', 'financial_year'])
    
    for lag in [1, 2, 3]:
        filtered_panel[f'value_lag{lag}'] = filtered_panel.groupby(['local_authority', 'size_category'])['value'].shift(lag)
    
    filtered_panel = filtered_panel.dropna(subset=['value'])
    
    return filtered_panel
