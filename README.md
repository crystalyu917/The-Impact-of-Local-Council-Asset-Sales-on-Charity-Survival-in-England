# The Impact of Local Council Asset Sales on Charity Survival in England

## Overview  
This repository contains the source materials for a dissertation submitted in August 2025 as part of the MSc Knowledge, Information and Data Science programme at University College London (UCL). The study was conducted in collaboration with the Social Investment Business through the Master’s Dissertation Scheme.  

This dissertation investigates whether local council asset sales, measured through capital receipt data, affect the survival of charities in England. Using Charity Commission deregistration records combined with local authority receipts, the study applies panel regression with fixed effects and temporal lags to identify both immediate and delayed effects.

## Environment & Installation
```bash
# install requirements
pip install -r requirements.txt

# (optional) install package in editable mode if using src/ for imports/console scripts
pip install -e.
```
## Project Structure
```bash
THE-CHANGE-IN-THE-UK-CHARITY-LANDSCAPE/
├── pyproject.toml
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── figures/
│   └── tables/
├── notebooks/
│   ├── charity_analysis.ipynb
│   ├── capital_receipt_analysis.ipynb
│   └── regression.ipynb
├── scripts/
│   ├── run_clean_charity.py
│   └── run_clean_receipt.py
└── src/
    └── cleaning/
        ├── __init__.py
        ├── clean_charity_main.py
        └── clean_receipt.py
```
## Datasets

Charity Commission. (2025). Register of charities: Full data download. Charity Commission for England and Wales. Retrieved April 2025, from https://register-of-charities.
charitycommission.gov.uk/en/register/full-register-download

DLUHC. (2024). Local authority capital expenditure, receipts and financing statistics [Formerly published by the Ministry of Housing, Communities & Local Government (2018–2021). Accessed: May 2025]. Department for Levelling Up, Housing, and Communities. https://www.gov.uk/government/collections/local-authority-capital-expenditure-receipts-
and-financing

Companies House. (2025). Free company data product [Accessed: April 2025]. Companies House. https://download.companieshouse.gov.uk/en_output.html

FindThatCharity. (2025). Findthatcharity webscraper [Accessed: April 2025]. FindThatCharity. https://findthatcharity.uk/

ONS. (2025). Postcode lookup to local authority codes [Accessed:  2025]. Office for National Statistics. https://www.ons.gov.uk/

## Results
This study examined the relationship between local authority asset disposals and the survival of charities in England between 2015 and 2023. By linking Charity Commission records with capital receipts data, the analysis applied fixed-effects panel models with lag structures to capture both contemporaneous and delayed associations. The findings reveal a clear size-based divergence. Large charities appear resilient, showing no immediate adverse effects and in some cases benefiting from disposals, while small charities face sustained increases in removals lasting up to three years, with the strongest effect at the two-year lag. Medium charities experience more modest, delayed impacts, becoming vulnerable only in the later years.

These patterns suggest that asset disposals create cumulative pressures that disproportionately affect organisations with limited reserves and weaker access to alternative premises. Each removal represents the loss of services, staff, and volunteers, meaning that even small statistical increases translate into significant social consequences when scaled nationally. The results also highlight the paradox of a sector numerically dominated by small and medium organisations but financially concentrated in a few large providers. Without targeted safeguards, such as measures to strengthen the capacity of smaller organisations to engage in CAT processes or preferential arrangements that prioritise community-scale actors, current disposal practices risk accelerating consolidation and diminishing the pluralism and resilience of local civil society. More broadly, the study demonstrates the value of integrating local authority financial data with charity-level outcomes, offering a scalable framework for assessing how shifts in public asset governance affect voluntary sector sustainability.

## Reproducibility
This repository contains the full code and cleaning scripts needed to replicate the analysis. Due to file size restrictions, raw datasets are not stored here but can be obtained from the listed sources.

Capital receipt data are manually collated by pasting each year from the original CSV as a separate tab into a combined file, which is then converted into a single CSV for easier processing and integration with the charity dataset.

