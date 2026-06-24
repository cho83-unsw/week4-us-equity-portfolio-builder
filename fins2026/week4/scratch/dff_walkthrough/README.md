# Week 4 lecture scripts --- Data Factory Floor (DFF)

These are the five scripts we run together in class. They take the project's
50-stock equity dataset through the Data Factory Floor: load and check the data,
build features (returns, risk, the Sharpe ratio, correlation), and construct
optimal portfolios.

## Set up your folder (do this before the lecture)

1. In your **fins-agent** repository, create the folder
   `fins2026/week4/scratch/dff_walkthrough/`.
2. Put all five files inside that folder:
   - `data_access.py` --- loads the 50-stock data (provided, do not edit)
   - `dff_helpers.py` --- small helpers for figures and tables
   - `01_stage1_etl.py` --- Stage 1: read, check, and reshape the data
   - `02_stage2_features.py` --- Stage 2: returns, risk, Sharpe, correlation
   - `03_stage3_portfolios.py` --- Stage 3: optimal portfolio weights
3. You do **not** add any data. `data_access.py` downloads the dataset
   (50 US stocks, 10 sectors, daily 2020-2023) automatically the first time you
   run a script, so you only need an internet connection.

## Run them in class

As we reach each stage, run that stage's script. Run them **in order**, because
Stage 2 and Stage 3 read what Stage 1 saved:

```
python 01_stage1_etl.py
python 02_stage2_features.py
python 03_stage3_portfolios.py
```

Run from inside the `dff_walkthrough/` folder, or open each file in PyCharm and
click the green **Run** button. The figures and tables each stage produces
appear in a new `output/` folder next to the scripts.

## If something does not run

- `No module named pandas` (or numpy / matplotlib) --- your course Python
  environment is not active. Activate it, or ask your AI assistant to install the
  missing package.
- A download error --- check your internet connection and run the script again.
  The data is cached after the first successful download, so later runs are fast.
