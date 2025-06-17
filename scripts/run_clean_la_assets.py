import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleaning.clean_la_assets import clean_la_assets

if __name__ == '__main__':
    la_files = [
        'data/raw/LocalAuthorityA-C_governmentCouncilOwnedAssets2025.xls',
        'data/raw/LocalAuthorityD-G_governmentCouncilOwnedAssets2025.xls',
        'data/raw/LocalAuthorityH-M_governmentCouncilOwnedAssets2025.xls',
        'data/raw/LocalAuthorityN-R_governmentCouncilOwnedAssets2025.xls',
        'data/raw/LocalAuthorityS-Z_governmentCouncilOwnedAssets2025.xls'
    ]

    la_name_file = 'data/raw/local_authority_names_and_codes_ONSPD2023.csv'

    df = clean_la_assets(la_files, la_name_file)
    output_path = 'data/processed/la_2025_asset_summary.csv'
    df.to_csv(output_path, index=False)

    print(f"✅ Cleaned LA asset summary saved to: {output_path}")
