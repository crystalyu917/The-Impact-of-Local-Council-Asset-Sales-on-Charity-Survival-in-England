import sys
import os
import pandas as pd

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleaning.clean_receipt import (
    YEAR_SKIP_MAPPING, 
    merge_columns, 
    unified_map, 
    flat_lookup, 
    non_england_keywords,
    clean_sheet, 
    rename_and_filter_disposal, 
    basic_cleaning, 
    merge_columns_func, 
    clean_local_authority, 
    apply_local_authority_cleaning, 
    filter_non_england, 
    melt_disposal, 
    create_complete_panel
)

DISPOSAL_FILEPATH = "data/raw/council_disposal_receipts.xlsx"
CHARITY_DATASET_PATH = "data/processed/charity_main_cleaned.csv"

# Step 1: Load disposal datasets
dfs = []
for year, skip_row in YEAR_SKIP_MAPPING.items():
    df = pd.read_excel(DISPOSAL_FILEPATH, skiprows=skip_row, sheet_name=year)
    dfs.append(df)

# Step 2: Clean sheets
dfs[0] = clean_sheet(dfs[0], rename_from_col=3, header_row=1)
dfs[1] = clean_sheet(dfs[1], rename_from_col=4, header_row=1)
dfs[2] = clean_sheet(dfs[2], rename_from_col=4, header_row=2)
dfs[3] = clean_sheet(dfs[3], rename_from_col=5, header_row=0)
dfs[4] = clean_sheet(dfs[4], rename_from_col=5, header_row=0)

for i in range(5, 10):
    dfs[i] = rename_and_filter_disposal(dfs[i], start_col=5 if i < 9 else 6)

# Step 3: Basic cleaning
dfs = [basic_cleaning(df, i) for i, df in enumerate(dfs)]

# Step 4: Merge columns
dfs = merge_columns_func(dfs, merge_columns)

# Step 5: Load charity dataset
charity_df = pd.read_csv(CHARITY_DATASET_PATH)

# Step 6: Local authority cleaning
dfs, charity_df = apply_local_authority_cleaning(dfs, charity_df, flat_lookup)

# Step 7: Filter out non-England charities
charity_df = filter_non_england(charity_df, non_england_keywords)

# Step 8: Melt disposal data
disposal_long_df = melt_disposal(dfs)

# Step 9: Create final panel dataset
final_panel = create_complete_panel(disposal_long_df, charity_df)

# Step 10: Export final dataset
final_panel.to_csv("data/processed/final_panel_data.csv", index=False)

print("Final panel dataset saved to data/processed/final_panel_data.csv")