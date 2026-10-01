# Finance Research Project

Quantitative and general finance research.

## Projects

### [`variance-ratio-study/`](variance-ratio-study/) — Random walks and what they cost to trade

Lo–MacKinlay variance ratio tests on the S&P 500 and four emerging markets (South
Africa, an Africa ex-SA proxy, Brazil, India) across three regimes — the GFC, COVID,
and the inflation cycle — followed by a transaction-cost study of the one trade the
statistics point at.

**Result:** 14 of 15 market-period combinations are statistically indistinguishable
from a random walk. The exception is the S&P 500 in 2008–2012 — the most liquid market
in the world, in its worst crisis, not any of the emerging markets. Its implied trade
clears real transaction costs (21.6% p.a. net of spreads, fees and borrow) but
collapses to near nothing when executed one day late. The edge is real, lives inside a
single closing print, and is gone by 2022.

See [the findings](variance-ratio-study/FINDINGS.md) ·
[the PDF](variance-ratio-study/reports/Transaction_Costs_Addendum.pdf) ·
[how to reproduce](variance-ratio-study/README.md)
