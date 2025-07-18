# cleaning/clean_disposal_charity_data.py

import pandas as pd
import numpy as np
import itertools

YEAR_SKIP_MAPPING = {
    "2014": 0, "2015": 0, "2016": 2, "2017": 3, "2018": 3,
    "2019": 4, "2020": 4, "2021": 4, "2022": 4, "2023": 4,
}

MERGE_COLUMNS = {
    "community safety": ["community safety", "community safety (cctv)"],
    # [Truncated for brevity, paste all mappings here exactly]
    "total culture & related services": ["culture & heritage"]
}

UNIFIED_MAP = {
    'buckinghamshire': ['aylesbury vale', 'chiltern', 'south bucks', 'wycombe','south buckinghamshire'],
    # [Truncated for brevity, paste all mappings here exactly]
}

NON_ENGLAND_KEYWORDS = [
    'aberdeen', 'aberdeenshire', 'angus', 'antrim', 'ards', # [Truncated]
    'channel islands'
]

FLAT_LOOKUP = {
    old.lower(): new.lower()
    for new, olds in UNIFIED_MAP.items()
    for old in olds
}

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
        if keyword in str(df.columns[i]):
            new_columns[i] = str(df.columns[i]).replace(keyword, "")
            cols_to_keep.append(i)
    df.columns = new_columns
    return df.iloc[:, cols_to_keep]

def clean_local_authority(name):
    if pd.isna(name): return name
    name = (str(name).lower().replace('&', 'and').replace('-', ' ').replace(',', '').replace('.', '')
            .replace(' city of', '').replace(' county of', '').strip())
    return FLAT_LOOKUP.get(name, name)

def clean_disposal_files(dfs):
    for idx, df in enumerate(dfs):
        df.columns = [str(col).strip().lower().replace(" and ", " & ") for col in df.columns]
        for standard_col, aliases in MERGE_COLUMNS.items():
            present_cols = [col for col in aliases if col in df.columns]
            if present_cols:
                df[standard_col] = df[present_cols].sum(axis=1, skipna=True)
                cols_to_drop = [col for col in present_cols if col != standard_col]
                df.drop(columns=cols_to_drop, inplace=True)
        if 'local_authority' in df.columns:
            df['local_authority'] = df['local_authority'].apply(clean_local_authority)
        dfs[idx] = df
    return dfs

def clean_charity_dataset(dataset):
    if 'local_authority' in dataset.columns:
        dataset['local_authority'] = dataset['local_authority'].apply(clean_local_authority)
    dataset['local_authority_lower'] = dataset['local_authority'].str.lower()
    dataset = dataset[~dataset['local_authority_lower'].str.contains('|'.join(NON_ENGLAND_KEYWORDS), na=False)]
    return dataset.drop(columns=['local_authority_lower'])

def melt_disposal(dfs):
    long_frames = []
    years = list(range(2014, 2024))
    for i, df in enumerate(dfs):
        if not df.empty:
            df['financial_year'] = years[i]
            long_df = df.melt(id_vars=["local_authority", "financial_year"], 
                value_vars=[c for c in df.columns if c not in ["ecode", 'lgf code', 'ons code', "class", "subclass", "local_authority", "financial_year", 'certification complete']], 
                var_name="category", value_name="value")
            long_frames.append(long_df)
    return pd.concat(long_frames, ignore_index=True)

def process_panel(disposal_long_df, dataset):
    disposal_long_df = disposal_long_df[disposal_long_df['category'] == 'all services total']
    disposal_long_df = disposal_long_df.groupby(['local_authority', 'financial_year', 'category']).agg({'value': 'sum'}).reset_index()
    removals = dataset.groupby(['local_authority', 'removal_fy', 'size_category']).size().reset_index(name='removals').rename(columns={'removal_fy': 'financial_year'})
    panel = pd.merge(disposal_long_df, removals, on=["financial_year", "local_authority"], how="outer")
    panel['removals'] = panel['removals'].fillna(0).astype(int)
    panel = panel[(panel['financial_year'] >= 2015) & (panel['financial_year'] <= 2023)]
    panel['value'] = pd.to_numeric(panel['value'], errors='coerce') / 1000
    unique_years = panel['financial_year'].unique()
    unique_authorities = panel['local_authority'].unique()
    unique_size_categories = panel['size_category'].dropna().unique()
    complete_index = pd.DataFrame(itertools.product(unique_years, unique_authorities, unique_size_categories), columns=['financial_year', 'local_authority', 'size_category'])
    complete_panel = pd.merge(complete_index, panel, on=['financial_year', 'local_authority', 'size_category'], how='left')
    complete_panel['removals'] = complete_panel['removals'].fillna(0).astype(int)
    complete_panel['value'] = complete_panel.groupby(['local_authority', 'financial_year'])['value'].transform('first')
    filtered_panel = complete_panel.drop(columns=['category'], errors='ignore').dropna(subset=['value']).sort_values(['local_authority', 'size_category', 'financial_year'])
    for lag in [1, 2, 3]:
        filtered_panel[f'value_lag{lag}'] = filtered_panel.groupby(['local_authority', 'size_category'])['value'].shift(lag)
    return filtered_panel