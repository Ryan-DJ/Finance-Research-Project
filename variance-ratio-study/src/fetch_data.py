"""Download daily closes for the five study markets from Yahoo Finance."""
import json, urllib.request, urllib.parse, datetime, csv, os
SYMS={"SPX":"^GSPC","JSE40":"^J200.JO","AFK":"AFK","IBOV":"^BVSP","NIFTY":"^NSEI"}
OUT=os.path.join(os.path.dirname(__file__),"..","data")
def main():
    p1=int(datetime.datetime(2007,11,1).timestamp()); p2=int(datetime.datetime(2026,8,28).timestamp())
    for k,s in SYMS.items():
        url=("https://query1.finance.yahoo.com/v8/finance/chart/"+urllib.parse.quote(s)+
             f"?period1={p1}&period2={p2}&interval=1d&events=div%2Csplit")
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        d=json.load(urllib.request.urlopen(req,timeout=60))
        r=d["chart"]["result"][0]; ts=r["timestamp"]; q=r["indicators"]["quote"][0]
        adj=r["indicators"].get("adjclose",[{}])[0].get("adjclose") if "adjclose" in r["indicators"] else None
        rows=[]
        for i,t in enumerate(ts):
            c=q["close"][i]; a=adj[i] if adj else c
            if c is None or a is None: continue
            rows.append((datetime.datetime.utcfromtimestamp(t).date().isoformat(),c,a))
        with open(os.path.join(OUT,k+".csv"),"w",newline="") as f:
            w=csv.writer(f); w.writerow(["date","close","adjclose"]); w.writerows(rows)
        print(k,s,r["meta"].get("currency"),len(rows),rows[0][0],rows[-1][0],flush=True)
if __name__=="__main__": main()
