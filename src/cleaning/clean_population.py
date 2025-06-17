import pandas as pd

def clean_population (pop_file: str, la_code_file: str) -> pd.DataFrame:
    """
    Merges population data with local authority names and returns a summary DataFrame.
    """
    population_data = pd.read_csv(pop_file)
    la_names = pd.read_csv(la_code_file)

    merged_df = pd.merge(
        population_data,
        la_names,
        left_on='Code',
        right_on='LAD23CD',
        how='left'
    )

    merged_df.rename(columns={
        'LAD23NM': 'local_authority',
        'All ages': 'population_count',
    }, inplace=True)

    population_summary = merged_df[['local_authority', 'population_count']]

    return population_summary