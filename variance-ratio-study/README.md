# Variance Ratio Study — S&P 500 vs Four Emerging Markets (2008–2026)

Are equity markets random walks? And where they are not, can the departure be traded
after costs?

Two linked studies:

1. **Random-walk tests.** Lo–MacKinlay variance ratios at four horizons, in three
   regimes, across five markets, with a Chow–Denning joint test and a wild bootstrap.
2. **Transaction-cost study.** The trade implied by the variance ratio result, charged
   every spread, commission, exchange fee, statutory tax and borrow cost it would
   really pay — plus a one-day execution-delay test.

Headline: **14 of 15 market-period combinations are statistically indistinguishable
from a random walk.** The one exception is the S&P 500 during 2008–2012 — the most
liquid market in the world, in its worst crisis. Its implied trade *does* clear
transaction costs (21.6% p.a. net), but collapses to 6.8% gross if executed a single
day late. The edge is real, lives entirely inside one closing print, and is gone by
2022.

Full write-up: **[FINDINGS.md](FINDINGS.md)** ·
PDF: **[reports/Transaction_Costs_Addendum.pdf](reports/Transaction_Costs_Addendum.pdf)**

---

## Markets

| Key | Market | Series | Currency |
|---|---|---|---|
| `SPX` | United States | S&P 500 (`^GSPC`) | USD |
| `JSE40` | South Africa | FTSE/JSE Top 40 (`^J200.JO`) | ZAR |
| `AFK` | Africa ex-SA | VanEck Africa Index ETF (`AFK`) | USD |
| `IBOV` | Brazil | Ibovespa (`^BVSP`) | BRL |
| `NIFTY` | India | Nifty 50 (`^NSEI`) | INR |

**On Nigeria.** Nigeria was the intended fourth emerging market. Daily NGX All-Share
history could not be obtained from any accessible source: the free providers do not
carry it, the paid APIs available here block non-US indices, and the only US-listed
Nigeria ETF (NGE) traded 2013–2021, covering none of the first window. `AFK` — a
GDP-weighted African basket whose largest weights are South Africa, Egypt, Morocco,
Nigeria and Kenya — stands in, with caveats stated throughout: it trades in New York
hours in USD, and ~2% of its days show a zero return, a stale-pricing signature that
mechanically biases its variance ratio below 1.

## Windows

| Window | Dates | Regime |
|---|---|---|
| `2008-2012` | 2008-01-01 → 2012-12-31 | GFC and Eurozone crisis |
| `2020-2021` | 2020-01-01 → 2021-12-31 | COVID shock and recovery |
| `2022-2026` | 2022-01-01 → 2026-08-27 | Inflation shock and post-cycle |
| `2020-2022*` | 2020-01-01 → 2022-12-31 | sensitivity check (overlapping) |

Windows are non-overlapping; the brief's "'20–'22 / '22–'26" is split at end-2021 so
2022 is not counted twice. The overlapping definition is run as a sensitivity and
changes no conclusion.

## Method

- **Lo & MacKinlay (1988)** variance ratio, overlapping q-period returns, unbiased
  estimator, at q = 2, 5, 10, 20 trading days.
- **z₁** (homoskedastic) reported only to show how badly it misleads; **z₂**
  (heteroskedasticity-robust) is the basis for every claim.
- **Chow & Denning (1993)** joint test — max |z₂| against the studentized maximum
  modulus, controlling joint size across the four horizons.
- **Kim (2006) wild bootstrap**, 2,000 replications, Mammen two-point weights,
  seed 42, for every p-value quoted.

Validation (`src/vrtest.py`, checked in `run_all.sh`): recovers theoretical variance
ratios on AR(1) and MA(1) processes; empirical size 7.2% (z₂) and 4.5% (joint) on
i.i.d. random walks at a nominal 5%; on a GARCH(1,1) random walk z₁ rejects 11.3% of
the time while z₂ holds at 5.7%.

## Transaction costs

All cost assumptions live in one file, [`src/costs.py`](src/costs.py), in basis points
per side. Statutory items are sourced in that file's docstring:

| | South Africa | India | Brazil | USA |
|---|---|---|---|---|
| Transaction tax | 0.25% on purchases (STT) | 0.10% both sides (delivery); 0.05% sell side (futures) | — | — |
| Exchange fees | ~0.5 bp | ~0.3 bp | 0.030% per side | ~0.2 bp |

Spreads, commissions and borrow rates are assumptions for a small institutional
account. Because they are assumptions, **every result is also reported as a breakeven
cost**, which depends on no assumption at all. Change the numbers in `costs.py` and
rerun to see your own answer.

## Reproducing

```bash
pip install -r requirements.txt
./run_all.sh
```

Runs in a couple of minutes. Fetches data from Yahoo Finance, reruns both studies,
regenerates every figure and the PDF report. All randomness is seeded, so the numbers
reproduce exactly — this repo's results were regenerated from scratch a month after
the original run and matched to the last decimal.

```
src/fetch_data.py     download daily closes
src/config.py         markets, windows, horizons, loaders
src/vrtest.py         Lo-MacKinlay / Chow-Denning / wild bootstrap
src/run_vr.py         study 1 -> results/vr_statistics.csv, sample_description.csv
src/costs.py          cost assumptions (edit me)
src/backtest.py       study 2 -> results/cost_backtest.csv, cost_sweep.csv
src/make_figures.py   all figures
src/build_report.py   PDF report
```

## Results files

| File | Contents |
|---|---|
| `results/vr_statistics.csv` | VR, z₁, z₂, asymptotic and bootstrap p-values, every market × window × horizon |
| `results/sample_description.csv` | sample stats and Chow–Denning joint tests |
| `results/cost_backtest.csv` | gross/cost/net returns, Sharpe, turnover, breakeven, drawdown |
| `results/cost_sweep.csv` | net return as a function of cost, 0–40 bps |

## Limitations

- Daily frequency only. Weekly sampling would cut microstructure noise; intraday would
  add it.
- No market-impact model. Results are for a small account; at size the closing-auction
  trade this strategy requires is a different problem.
- The traded strategy was chosen *after* the variance ratio test pointed at it, so its
  t-statistics are optimistic.
- Two African-linked series is not a test of African market efficiency.

## References

Lo, A. W. & MacKinlay, A. C. (1988). *Stock market prices do not follow random walks.*
Review of Financial Studies 1(1), 41–66.
Chow, K. V. & Denning, K. C. (1993). *A simple multiple variance ratio test.*
Journal of Econometrics 58(3), 385–401.
Kim, J. H. (2006). *Wild bootstrapping variance ratio tests.* Economics Letters 92(1), 38–43.
