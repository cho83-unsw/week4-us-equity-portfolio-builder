# SpaceX IPO data --- Week 4 practise exercise

This is the SpaceX share-price data for the Week 4 practise exercise. It is a
frozen snapshot, so your numbers will match the lecture slides exactly.

## Set up your folder

1. In your course repository, create the folder
   `fins2026/week4/scratch/spacex_ipo/`.
2. Put these data files and this README inside that folder.
3. Write your own Python in the same folder, and save your figures and tables
   under `fins2026/week4/scratch/spacex_ipo/output/`.

## The files

- `spcx_hourly.csv` / `.parquet` --- hourly close and return, 11 to 22 June 2026.
  The 11 June row is the $135 IPO offer price, added as the starting point, so
  the first return is the IPO pop.
- `spcx_5min.csv` / `.parquet` --- five-minute close and return, 12 to 22 June 2026.

Each file has three columns: `datetime`, `close`, and `return`. Prices are in
US dollars on a New York clock. The window covers SpaceX's first six trading
days on the Nasdaq under the ticker SPCX (19 June was a US holiday). The CSV and
Parquet versions hold the same data --- use whichever you prefer
(`pandas.read_csv` or `pandas.read_parquet`).

## Your task

Turn this data into one clear narrative about how SpaceX performed and whether
it was a good investment once you account for risk. Use the skills from Weeks 1
to 3: simple returns, the growth of $1, volatility, and the Sharpe ratio.
Support your claim with numbers and a small number of clear, professional
figures.

For a benchmark comparison, download a second series yourself (for example
Tesla, Nvidia, or the Nasdaq-100) using the tools from earlier weeks. That
series is live data and will not be frozen, so report the date you downloaded
it.
