# Findings

Two studies. The first asks whether five equity markets behave like random walks. The
second asks whether the one place they don't can be traded after costs.

---

## Study 1 — Are these markets random walks?

### 1. The random walk survives almost everywhere

Sixty individual variance ratio statistics (5 markets × 3 windows × 4 horizons) and
fifteen joint tests. Under the heteroskedasticity-robust statistic with wild-bootstrap
p-values, **5 of 60** individual statistics reject at 5%, and **1 of 15** joint
Chow–Denning tests rejects: the S&P 500 in 2008–2012 (MV = 2.52, bootstrap p = 0.044).

| Market | 2008–2012 | 2020–2021 | 2022–2026 |
|---|---|---|---|
| S&P 500 | **0.044** | 0.067 | 0.677 |
| JSE Top 40 | 0.312 | 0.919 | 0.119 |
| Africa ETF | 0.170 | 0.440 | 0.093 |
| Ibovespa | 0.338 | 0.182 | 0.739 |
| Nifty 50 | 0.333 | 0.629 | 0.843 |

*Chow–Denning joint test, wild-bootstrap p-values. Bold = rejects at 5%.*

### 2. The efficiency ranking is the opposite of the textbook prior

Averaged across horizons, the S&P 500 is the *furthest* from a random walk in both
crisis windows (mean |VR − 1| of 0.24 in each) against 0.05–0.21 for the four emerging
markets. The usual assumption — that thin, less-regulated emerging markets should show
more exploitable serial dependence than the deepest market on earth — is not supported
at daily frequency in these windows.

Two mechanisms plausibly explain it. The S&P 500 in 2008 and 2020 was where global risk
was actually repriced: forced deleveraging and margin calls generate exactly the
short-horizon overshoot-and-correct that VR < 1 detects, and they generate it at index
level. And statistical power is not neutral — emerging index returns are noisier, so
the same dependence is harder to detect there. The honest reading is *"the evidence
does not distinguish the emerging markets from a random walk"*, not *"the emerging
markets are efficient"*.

### 3. Assuming homoskedasticity would have quadrupled the findings

The naive statistic z₁ rejects **19 of 60** times; the robust z₂ rejects **5**. The
fourteen casualties are volatility clustering misread as predictability. The most
spectacular: the S&P 500 at q = 2 in 2020–2021, where z₁ = −6.98 (p < 10⁻¹¹) collapses
to z₂ = −2.27; Brazil in the same window goes from z₁ = −5.53 to z₂ = −1.67 — decisive
rejection to no evidence at all.

Simulation confirms the mechanism: on a GARCH(1,1) random walk, z₁ rejects 11.3% of the
time at a nominal 5% while z₂ holds at 5.7%.

**Practical consequence:** any efficiency study over a crisis sample that reports the
homoskedastic statistic is measuring volatility dynamics, not predictability.

### 4. The sign of the deviation rotates with the regime, not the market

- **2008–2012** — mean-reverting almost everywhere (cross-market mean VR(10) = 0.82).
  The S&P 500's VR(10) = 0.69 means two-week return variance was 31% below what
  independent daily increments would produce. India is the lone exception.
- **2020–2021** — splits by horizon. The S&P 500 reverses violently day to day
  (VR(2) = 0.69, the largest deviation in the study, bootstrap p = 0.013) while all four
  emerging markets turn VR > 1 at 10–20 days (AFK 1.51, Nifty 1.32), i.e. multi-week
  trending during the liquidity-driven recovery. None of the latter are significant —
  ~500 observations is thin at q = 20 — but the sign is unanimous.
- **2022–2026** — the quietest window. Every VR(2) sits within 0.07 of unity.

---

## Study 2 — Does it survive transaction costs?

The trade implied by VR < 1: **bet against the last move**. Full position, every day,
no filters. Also run as a weekly version (5-day signal, weekly rebalance).

### 5. In the cheapest market it clears costs — which corrects the first report

| | gross % p.a. | costs | net | net Sharpe | t-stat | breakeven | charged |
|---|---|---|---|---|---|---|---|
| S&P 500, 2008–2012 | 24.4 | 2.8 | **21.6** | 0.82 | 2.07 | 9.5 bps | 1.0 bps |
| S&P 500, 2020–2021 | 31.6 | 3.1 | **28.6** | 1.09 | 1.71 | 11.4 bps | 1.0 bps |
| S&P 500, 2022–2026 | 7.0 | 2.8 | 4.3 | 0.25 | 0.88 | 2.8 bps | 1.0 bps |
| Ibovespa, 2020–2021 | 55.4 | 26.4 | **29.0** | 0.82 | 2.20 | 19.6 bps | 9.0 bps |

The first report called the significant finding "not tradeable" on the basis of costs
in the abstract. Having actually charged them, that was too strong: in the S&P 500 the
trade needs costs below 9.5 bps per leg and pays about 1.0. It clears, with room.

Note Brazil 2020–2021: the trade made money (t = 2.20) where the variance ratio test
found nothing significant. The strategy's P&L concentrates in a handful of violent
COVID days; the robust VR statistic is built to discount exactly those days. Over two
years it is not obvious which of the two is right.

### 6. Everywhere else, taxes decide it

A strategy that flips position daily turns over ~250× its own notional per year. At
South Africa's 26 bps all-in that is 250 × 26 bps = **65% a year in costs**, against
gross returns in the single digits.

| Market | daily trade, cash shares | via index futures |
|---|---|---|
| JSE Top 40, 2008–2012 | −70.7% p.a. | −18.2% |
| Africa ETF, 2008–2012 | −48.5% | no futures market |
| Nifty 50, 2022–2026 | −52.7% | −29.0% |

South Africa's 0.25% transfer tax on every purchase and India's 0.10% STT on both sides
of delivery trades are the dominant terms. Index futures escape the share-transfer
taxes and roughly quarter the cost — still losing. The weekly version trades a fifth as
often and turns a few combinations mildly positive (South Africa and India via
futures), but at t-statistics of 1.1–1.3, which is the signature of noise.

### 7. The test that actually kills it

Every result above assumes execution at the exact closing price that generated the
signal. Rerun with a one-day delay:

| | at the close | one day later |
|---|---|---|
| S&P 500, 2008–2012 | +23.0% p.a. | +5.4% |
| S&P 500, 2020–2021 | +30.1% | **−28.7%** |
| Ibovespa, 2020–2021 | +44.1% | **−36.0%** |

*(futures implementation, so the comparison is about timing and not fees)*

The entire edge lives inside one closing print and is gone within 24 hours. That is not
a fee problem and no amount of cost engineering fixes it — it is a statement about how
fast prices absorbed information during a panic. Monetising it would mean competing for
the closing auction against firms whose whole business is competing for the closing
auction.

### 8. What would have to be true to believe it

- **Measured fills at the close, at size, in 2008-style conditions** — not assumed ones.
- **A better t-statistic than 2.07 over five years**, bearing in mind the strategy was
  chosen *after* the VR test pointed at that market and window.
- **Out-of-sample survival.** It half-survives: still works in 2020–2021 (t = 1.71),
  gone by 2022–2026 (t = 0.88). A pattern that only pays in crises is a bet on the next
  crisis.
- **A capacity model.** Nothing here models market impact, which at scale would be the
  dominant cost and is in none of these tables.

---

## Data note

Nigeria is represented by the `AFK` ETF because daily NGX All-Share history was not
obtainable from any accessible source. It trades in USD during New York hours, and ~2%
of its days show a zero return — stale pricing that mechanically pulls its variance
ratio below 1 and probably explains its one individually significant result
(q = 2, 2022–2026). Proper daily African index data requires a paid feed.
