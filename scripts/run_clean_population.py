import sys
import os
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cleaning.clean_population import clean_population

if __name__ == '__main__':
    pop_path = 'data/raw/populationData_Census2023.csv'
    la_code_path = 'data/raw/local_authority_names_and_codes_ONSPD2023.csv'
    output_path = 'data/processed/population_summary_by_la.csv'

    df = clean_population(pop_path, la_code_path)
    df.to_csv(output_path, index=False)

    print(f"✅ Population summary saved to: {output_path}")
