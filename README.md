# The Impact of Local Council Asset Sales on Charity Survival in England

## Overview  
This repository contains the source materials for a dissertation submitted in August 2025 as part of the MSc Knowledge, Information and Data Science programme at University College London (UCL).  

The study was conducted in collaboration with the Social Investment Business through the Master’s Dissertation Scheme.  

## Environment & Installation
```bash
# install requirements
pip install -r requirements.txt

# (optional) install package in editable mode if using src/ for imports/console scripts
pip install -e .
```
## Project Structure
```bash
THE-CHANGE-IN-THE-UK-CHARITY-LANDSCAPE/
├─ pyproject.toml
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  ├─ raw/
│  └─ processed/
├─ outputs/
│  ├─ figures/
│  └─ tables/
├─ notebooks/
│  ├─ charity_analysis.ipynb
│  ├─ capital_receipt_analysis.ipynb
│  └─ regression.ipynb
├─ scripts/
│  ├─ run_clean_charity.py
│  └─ run_clean_receipt.py
└─ src/
  ├─ cleaning/
  │  ├─ __init__.py
  │  ├─ clean_charity_main.py
  │  └─ clean_receipt.py
  ├─ io.py
  └─ config.py
```
## Datasets
