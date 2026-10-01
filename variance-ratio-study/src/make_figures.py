"""All figures for the study."""
import numpy as np, pandas as pd, os, sys, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(__file__))
from config import MARKETS, PERIODS, MAIN_PERIODS, QS, RESULTS, FIGS, load_prices
from costs import CASH, FUTURES, one_way
from backtest import signal

plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.edgecolor":"#9aa3ae","axes.linewidth":.7,
 "axes.grid":True,"grid.color":"#e3e7ec","grid.linewidth":.7,"axes.axisbelow":True,"figure.dpi":200,"savefig.dpi":200})
C={"SPX":"#2f4b7c","JSE40":"#d1495b","AFK":"#e08a1e","IBOV":"#2a9d8f","NIFTY":"#7b5ea7"}
L={"SPX":"S&P 500 (US)","JSE40":"JSE Top 40 (ZA)","AFK":"Africa ETF (AFK)","IBOV":"Ibovespa (BR)","NIFTY":"Nifty 50 (IN)"}
PT={"2008-2012":"2008–2012  ·  GFC & Euro crisis","2020-2021":"2020–2021  ·  COVID shock & recovery",
    "2022-2026":"2022–2026  ·  Inflation & post-cycle"}
NAVY="#22303f"

def vr_figures():
    v=pd.read_csv(os.path.join(RESULTS,"vr_statistics.csv"))
    fig,axes=plt.subplots(1,3,figsize=(11,3.5),sharey=True)
    for ax,p in zip(axes,MAIN_PERIODS):
        sub=v[v.period==p]; ax.axhline(1,color="#333",lw=1,ls=(0,(4,3)),zorder=1)
        for m in C:
            s=sub[sub.mkt==m].sort_values("q")
            if s.empty: continue
            ax.plot(s.q,s.vr,color=C[m],lw=1.6,marker="o",ms=4,label=L[m],zorder=3)
            sig=s[s.boot_p<0.05]
            ax.scatter(sig.q,sig.vr,s=95,facecolor=C[m],edgecolor="#111",lw=1.3,zorder=5)
        ax.set_title(PT[p],fontsize=9.5,loc="left",color=NAVY,pad=7)
        ax.set_xlabel("holding period q (trading days)"); ax.set_xticks(QS); ax.set_xlim(1,21)
    axes[0].set_ylabel("Variance ratio  VR(q)"); axes[0].set_ylim(0.6,1.6)
    axes[0].legend(frameon=False,fontsize=8,loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(FIGS,"vr_profiles.png"),bbox_inches="tight"); plt.close(fig)

def cost_sweep_figure():
    sw=pd.read_csv(os.path.join(RESULTS,"cost_sweep.csv"))
    fig,axes=plt.subplots(1,3,figsize=(11,3.4),sharey=True)
    for ax,p in zip(axes,MAIN_PERIODS):
        ax.axhline(0,color=NAVY,lw=1.2,zorder=2)
        for m in C:
            s=sw[(sw.period==p)&(sw.mkt==m)]
            if s.empty: continue
            ax.plot(s.cost_bps,s.net_ann,color=C[m],lw=1.7,label=L[m],zorder=3)
            c=CASH[m]; actual=0.5*(one_way(c,"buy")+one_way(c,"sell"))
            y=np.interp(actual,s.cost_bps,s.net_ann)
            ax.scatter([actual],[y],s=70,color=C[m],edgecolor="white",lw=1.2,zorder=5)
        ax.set_xlim(0,40); ax.set_xlabel("cost charged per unit traded (bps)")
        ax.set_title(PT[p],fontsize=9.5,loc="left",color=NAVY,pad=7)
    axes[0].set_ylabel("Net return of the reversal trade (% p.a.)"); axes[0].set_ylim(-110,70)
    axes[0].legend(frameon=False,fontsize=8,loc="lower left")
    fig.text(0.5,-0.045,"Where a line crosses zero is that market's breakeven cost. If its dot sits left of the crossing the trade pays; right of it, the trade loses.",
             ha="center",fontsize=7.6,color="#5a6673")
    fig.tight_layout(); fig.savefig(os.path.join(FIGS,"cost_sweep.png"),bbox_inches="tight"); plt.close(fig)

def waterfall_figure():
    bt=pd.read_csv(os.path.join(RESULTS,"cost_backtest.csv"))
    d=bt[(bt.variant=="daily reversal")&(bt.impl=="cash/ETF")]
    fig,axes=plt.subplots(1,3,figsize=(11,3.1),sharey=True)
    mk=list(C.keys())
    for ax,p in zip(axes,MAIN_PERIODS):
        s=d[d.period==p].set_index("mkt")
        x=np.arange(len(mk))
        g=[s.gross_ann.get(m,np.nan) for m in mk]; c=[-s.cost_ann.get(m,np.nan) for m in mk]
        n=[s.net_ann.get(m,np.nan) for m in mk]
        ax.bar(x-0.26,g,0.26,color="#9fb3cc",label="gross profit")
        ax.bar(x,c,0.26,color="#d1495b",label="costs")
        ax.bar(x+0.26,n,0.26,color=NAVY,label="net")
        ax.axhline(0,color=NAVY,lw=1)
        ax.set_xticks(x,[L[m].split(" (")[0] for m in mk],fontsize=7.5,rotation=20,ha="right")
        ax.set_title(PT[p],fontsize=9.5,loc="left",color=NAVY,pad=7)
    axes[0].set_ylabel("% per year"); axes[0].set_ylim(-110,70)
    axes[0].legend(frameon=False,fontsize=8,loc="lower left")
    fig.tight_layout(); fig.savefig(os.path.join(FIGS,"cost_waterfall.png"),bbox_inches="tight"); plt.close(fig)

def equity_figure():
    px=load_prices("SPX"); a,b=PERIODS["2008-2012"]; s=px.loc[a:b]
    ret=np.diff(np.log(s.values)); idx=s.index[1:]
    w=signal(ret,1,1); wl=signal(ret,1,1,lag=1)
    dw=np.abs(np.diff(np.concatenate([[0.0],w]))); dwl=np.abs(np.diff(np.concatenate([[0.0],wl])))
    cc=0.5*(one_way(CASH["SPX"],"buy")+one_way(CASH["SPX"],"sell"))/1e4
    bw=np.where(w<0,CASH["SPX"]["borrow"]/1e4/252,0.0)
    curves={"Buy & hold the index":ret,
            "Reversal trade, before costs":w*ret,
            "Reversal trade, after real costs":w*ret-dw*cc-bw,
            "Same trade, executed one day late":wl*ret-dwl*cc-np.where(wl<0,CASH["SPX"]["borrow"]/1e4/252,0.0)}
    col={"Buy & hold the index":"#8b95a1","Reversal trade, before costs":"#9fb3cc",
         "Reversal trade, after real costs":"#2f4b7c","Same trade, executed one day late":"#d1495b"}
    fig,ax=plt.subplots(figsize=(8.2,3.4))
    for k,r in curves.items():
        ax.plot(idx,100*np.cumprod(1+r),color=col[k],lw=2.0 if "after real" in k else 1.5,label=k)
    ax.set_ylabel("value of $100"); ax.legend(frameon=False,fontsize=8.5,loc="upper left")
    ax.set_title("The best case in the whole study: S&P 500, 2008–2012",loc="left",color=NAVY,fontsize=10.5,pad=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIGS,"equity_spx_0812.png"),bbox_inches="tight"); plt.close(fig)

if __name__=="__main__":
    os.makedirs(FIGS,exist_ok=True)
    vr_figures(); cost_sweep_figure(); waterfall_figure(); equity_figure(); print("figures written")
