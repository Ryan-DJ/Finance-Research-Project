import os, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data"); RESULTS = os.path.join(ROOT, "results"); FIGS = os.path.join(ROOT, "figures")

# key: (country, index name, currency, price column to use)
MARKETS = {
    "SPX":   ("United States", "S&P 500",                   "USD", "close"),
    "JSE40": ("South Africa",  "FTSE/JSE Top 40",           "ZAR", "close"),
    "AFK":   ("Africa ex-SA",  "VanEck Africa Index ETF",   "USD", "adjclose"),
    "IBOV":  ("Brazil",        "Ibovespa",                  "BRL", "close"),
    "NIFTY": ("India",         "Nifty 50",                  "INR", "close"),
}
PERIODS = {
    "2008-2012":  ("2008-01-01", "2012-12-31"),
    "2020-2021":  ("2020-01-01", "2021-12-31"),
    "2022-2026":  ("2022-01-01", "2026-08-27"),
    "2020-2022*": ("2020-01-01", "2022-12-31"),   # sensitivity: overlapping window
}
MAIN_PERIODS = ["2008-2012", "2020-2021", "2022-2026"]
QS = [2, 5, 10, 20]

def load_prices(key):
    col = MARKETS[key][3]
    df = pd.read_csv(os.path.join(DATA, key + ".csv"), parse_dates=["date"]).set_index("date")
    return df[col].dropna()
