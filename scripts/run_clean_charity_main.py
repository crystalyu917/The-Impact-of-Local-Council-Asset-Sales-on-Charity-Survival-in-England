import sys
import os

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleaning.clean_charity_main import clean_charity_main

if __name__ == '__main__':
    input_path = 'data/raw/charities_RegisteredCharitiesInEnglandAndWales2025.csv'
    output_path = 'data/processed/charity_main_cleaned.csv'

    df = clean_charity_main(input_path)
    df.to_csv(output_path, index=False)

    print(f"✅ Cleaned dataset saved to: {output_path}")
    # print(f"Total charities: {len(df):,}")
    # print(f"Active: {(df['charity_status'] == 'active').sum():,}")
    # print(f"Inactive: {(df['charity_status'] == 'inactive').sum():,}")
