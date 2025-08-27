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


## Reproducibility
This repository contains the full code and cleaning scripts needed to replicate the analysis. Due to file size restrictions, raw datasets are not stored here but can be obtained from the listed sources.

Capital receipt data are manually collated by pasting each year from the original CSV as a separate tab into a combined file, which is then converted into a single CSV for easier processing and integration with the charity dataset.

