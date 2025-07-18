# run_disposal_panel.py

import pandas as pd
from cleaning.clean_receipt import YEAR_SKIP_MAPPING, clean_sheet, rename_and_filter_disposal, clean_disposal_files, clean_charity_dataset, melt_disposal, process_panel

DISPOSAL_FILEPATH = "../../data/raw/council_disposal_receipts.xlsx"
CHARITY_DATASET_PATH = "../../data/processed/charity_main_cleaned.csv"

dfs = []
for year, skip_row in YEAR_SKIP_MAPPING.items():
    df = pd.read_excel(DISPOSAL_FILEPATH, skiprows=skip_row, sheet_name=year)
    dfs.append(df)

# Clean sheets
dfs[0] = clean_sheet(dfs[0], rename_from_col=3, header_row=1)
dfs[1] = clean_sheet(dfs[1], rename_from_col=4, header_row=1)
dfs[2] = clean_sheet(dfs[2], rename_from_col=4, header_row=2)
dfs[3] = clean_sheet(dfs[3], rename_from_col=5, header_row=0)
dfs[4] = clean_sheet(dfs[4], rename_from_col=5, header_row=0)

for i in range(5, 10):
    dfs[i] = rename_and_filter_disposal(dfs[i], start_col=5 if i < 9 else 6)

dfs = clean_disposal_files(dfs)

charity_df = pd.read_csv(CHARITY_DATASET_PATH)
charity_df = clean_charity_dataset(charity_df)

disposal_long_df = melt_disposal(dfs)
filtered_panel = process_panel(disposal_long_df, charity_df)

filtered_panel.to_csv("../../data/processed/final_panel_data.csv", index=False)
