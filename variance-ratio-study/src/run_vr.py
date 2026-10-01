"""Run the variance ratio battery across markets and sub-periods."""
import numpy as np, pandas as pd, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vrtest import vr_stats, chow_denning, wild_bootstrap
from config import MARKETS, PERIODS, QS, DATA, RESULTS, load_prices

def main():
    rows, desc = [], []
    for k in MARKETS:
        px = load_prices(k)
        for pname, (a, b) in PERIODS.items():
            s = px.loc[a:b]
            if len(s) < 60: continue
            lp = np.log(s.values); ret = np.diff(lp)
            mv, cdp, _ = chow_denning(lp, QS)
            bp, bjoint = wild_bootstrap(ret, QS, nboot=2000, seed=42)
            desc.append(dict(mkt=k, period=pname, n=len(ret), start=str(s.index[0].date()),
                end=str(s.index[-1].date()), ann_ret=float(ret.mean()*252*100),
                ann_vol=float(ret.std(ddof=1)*np.sqrt(252)*100),
                skew=float(pd.Series(ret).skew()), kurt=float(pd.Series(ret).kurt()),
                ac1=float(pd.Series(ret).autocorr(1)), zero_pct=float(np.mean(np.abs(ret)<1e-12)*100),
                cd_mv=mv, cd_p=cdp, cd_boot_p=bjoint))
            for q in QS:
                st = vr_stats(lp, q)
                rows.append(dict(mkt=k, period=pname, q=q, n=st['n'], vr=st['vr'], z1=st['z1'],
                                 p1=st['p1'], z2=st['z2'], p2=st['p2'], boot_p=bp[q]))
            print(k, pname, "done", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "vr_statistics.csv"), index=False)
    pd.DataFrame(desc).to_csv(os.path.join(RESULTS, "sample_description.csv"), index=False)

if __name__ == "__main__": main()
