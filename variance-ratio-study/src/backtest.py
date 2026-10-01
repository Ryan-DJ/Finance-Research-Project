"""Does the variance-ratio pattern survive transaction costs?

Strategy: contrarian (the trade a VR < 1 implies) -- bet against the last
move, because a zig-zag market partially reverses it.
  daily  : w_t = -sign(return over the previous 1 day),  rebalanced daily
  weekly : w_t = -sign(return over the previous 5 days), rebalanced every 5 days
Positions are +-1 of notional. Costs are charged on |w_t - w_{t-1}| notional
traded, split into the buy and sell legs, plus a borrow fee on short days.
"""
import numpy as np, pandas as pd, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from config import MARKETS, PERIODS, MAIN_PERIODS, RESULTS, load_prices
from costs import CASH, FUTURES, one_way, round_trip

def signal(ret, lookback, rebalance, lag=0):
    """Contrarian weights. w[t] uses returns through t-1-lag only.
    lag=0 assumes you can trade at the close that produced the signal
    (market-on-close); lag=1 assumes you only get in a day later."""
    n = len(ret); w = np.zeros(n); cur = 0.0
    start = lookback + lag
    for t in range(n):
        if t < start:
            w[t] = 0.0; continue
        if (t - start) % rebalance == 0:
            cur = -np.sign(np.sum(ret[t - lookback - lag:t - lag]))
        w[t] = cur
    return w

def run(ret, w, c):
    """Gross and net P&L. Costs in bps -> decimals."""
    n = len(ret)
    gross = w * ret
    dw = np.abs(np.diff(np.concatenate([[0.0], w])))          # notional traded each day
    # a flip from -1 to +1 trades 2 units: 1 unit buy-to-cover + 1 unit buy, etc.
    # charge the average of the buy and sell leg, which is what a flip costs per unit
    avg_leg = 0.5 * (one_way(c, "buy") + one_way(c, "sell")) / 1e4
    trade_cost = dw * avg_leg
    borrow = np.where(w < 0, c["borrow"] / 1e4 / 252.0, 0.0)
    net = gross - trade_cost - borrow
    return gross, net, trade_cost, borrow, dw

def summarise(ret, w, c, label):
    gross, net, tc, bw, dw = run(ret, w, c)
    n = len(ret); ann = 252.0
    g_mu = gross.mean(); t_stat = g_mu / (gross.std(ddof=1) / np.sqrt(n)) if gross.std() > 0 else 0.0
    turn = dw.mean()
    breakeven = (g_mu / turn * 1e4) if turn > 0 else np.nan   # bps per unit traded (avg leg)
    eq = np.cumprod(1 + net); dd = float((eq / np.maximum.accumulate(eq) - 1).min())
    return dict(variant=label, n=n,
                gross_ann=g_mu * ann * 100, cost_ann=(tc.mean() + bw.mean()) * ann * 100,
                net_ann=net.mean() * ann * 100,
                gross_sharpe=g_mu / gross.std(ddof=1) * np.sqrt(ann) if gross.std() > 0 else np.nan,
                net_sharpe=net.mean() / net.std(ddof=1) * np.sqrt(ann) if net.std() > 0 else np.nan,
                t_gross=t_stat, ann_turnover=turn * ann,
                charged_bps=0.5 * (one_way(c, "buy") + one_way(c, "sell")),
                breakeven_bps=breakeven, max_dd=dd * 100,
                hit_rate=float((gross > 0).mean() * 100))

def main():
    out = []
    for k in MARKETS:
        px = load_prices(k)
        for p in MAIN_PERIODS:
            a, b = PERIODS[p]
            s = px.loc[a:b]
            ret = np.diff(np.log(s.values))
            bh = dict(mkt=k, period=p, impl="buy & hold", variant="buy & hold", n=len(ret),
                      gross_ann=ret.mean()*252*100, cost_ann=0.0, net_ann=ret.mean()*252*100,
                      gross_sharpe=ret.mean()/ret.std(ddof=1)*np.sqrt(252),
                      net_sharpe=ret.mean()/ret.std(ddof=1)*np.sqrt(252),
                      t_gross=ret.mean()/(ret.std(ddof=1)/np.sqrt(len(ret))),
                      ann_turnover=0.0, charged_bps=0.0, breakeven_bps=np.nan,
                      max_dd=float((np.cumprod(1+ret)/np.maximum.accumulate(np.cumprod(1+ret))-1).min())*100,
                      hit_rate=float((ret>0).mean()*100))
            out.append(bh)
            for impl, table in (("cash/ETF", CASH), ("futures", FUTURES)):
                c = table[k]
                if c is None: continue
                for label, lb, rb, lg in (("daily reversal", 1, 1, 0),
                                          ("daily reversal, 1-day late", 1, 1, 1),
                                          ("weekly reversal", 5, 5, 0)):
                    w = signal(ret, lb, rb, lg)
                    row = summarise(ret, w, c, label); row.update(mkt=k, period=p, impl=impl)
                    out.append(row)
    df = pd.DataFrame(out)[["mkt","period","impl","variant","n","gross_ann","cost_ann","net_ann",
        "gross_sharpe","net_sharpe","t_gross","ann_turnover","charged_bps","breakeven_bps","max_dd","hit_rate"]]
    df.to_csv(os.path.join(RESULTS, "cost_backtest.csv"), index=False)
    print(df.round(2).to_string(index=False))
    sweep()

def sweep():
    """Net annualised return of the daily reversal trade as a function of the
    one-way cost charged, independent of any cost assumption."""
    rows = []
    grid = np.arange(0, 40.5, 0.5)
    for k in MARKETS:
        px = load_prices(k)
        for p in MAIN_PERIODS:
            a, b = PERIODS[p]
            ret = np.diff(np.log(px.loc[a:b].values))
            w = signal(ret, 1, 1)
            gross = (w * ret)
            dw = np.abs(np.diff(np.concatenate([[0.0], w])))
            for c in grid:
                net = gross - dw * c / 1e4
                rows.append(dict(mkt=k, period=p, cost_bps=c, net_ann=net.mean() * 252 * 100))
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "cost_sweep.csv"), index=False)
    print("cost sweep written")

if __name__ == "__main__": main()
