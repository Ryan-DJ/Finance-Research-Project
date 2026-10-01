"""Build the transaction-cost addendum PDF (HTML -> chromium print)."""
import pandas as pd, numpy as np, base64, datetime, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from config import RESULTS, FIGS, ROOT, MAIN_PERIODS
from costs import CASH, FUTURES, one_way

L={"SPX":"S&amp;P 500 (US)","JSE40":"JSE Top 40 (South Africa)","AFK":"Africa ETF (AFK)","IBOV":"Ibovespa (Brazil)","NIFTY":"Nifty 50 (India)"}
ORDER=["SPX","JSE40","AFK","IBOV","NIFTY"]
bt=pd.read_csv(os.path.join(RESULTS,"cost_backtest.csv"))
def img(p): return "data:image/png;base64,"+base64.b64encode(open(os.path.join(FIGS,p),'rb').read()).decode()

def cost_table():
    h=['<table class="t"><thead><tr><th class="l" rowspan="2">Market</th><th colspan="6">Cash shares / ETF, one-way bps</th><th colspan="2">Index futures</th></tr>',
       '<tr><th>half<br>spread</th><th>comm.</th><th>fees</th><th>tax<br>buy</th><th>tax<br>sell</th><th class="tot">all-in<br>per leg</th><th>all-in<br>per leg</th><th>borrow<br>saved</th></tr></thead><tbody>']
    for m in ORDER:
        c=CASH[m]; f=FUTURES[m]
        avg=0.5*(one_way(c,"buy")+one_way(c,"sell"))
        favg="%.2f"%(0.5*(one_way(f,"buy")+one_way(f,"sell"))) if f else "no market"
        h.append('<tr><td class="l">%s</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td>%.1f</td><td class="tot">%.2f</td><td>%s</td><td>%d bps/yr</td></tr>'
                 %(L[m],c["half_spread"],c["commission"],c["fees"],c["tax_buy"],c["tax_sell"],avg,favg,c["borrow"]))
    h.append('</tbody></table>'); return "".join(h)

def results_table(variant):
    d=bt[bt.variant==variant]
    h=['<table class="t"><thead><tr><th class="l" rowspan="2">Market</th><th class="l" rowspan="2">Window</th><th colspan="4">Cash shares / ETF</th><th colspan="2">Futures</th><th rowspan="2">t-stat</th><th rowspan="2">breakeven<br>bps/leg</th></tr>',
       '<tr><th>gross<br>%&nbsp;p.a.</th><th>costs<br>%&nbsp;p.a.</th><th>net<br>%&nbsp;p.a.</th><th>net<br>Sharpe</th><th>net<br>%&nbsp;p.a.</th><th>net<br>Sharpe</th></tr></thead><tbody>']
    for m in ORDER:
        for i,p in enumerate(MAIN_PERIODS):
            c=d[(d.mkt==m)&(d.period==p)&(d.impl=="cash/ETF")]
            f=d[(d.mkt==m)&(d.period==p)&(d.impl=="futures")]
            if c.empty: continue
            c=c.iloc[0]
            cls=' class="grp"' if i==0 and m!="SPX" else ''
            win=lambda v,s=' class="win"': s if v>0 else ''
            fn="%.1f"%f.net_ann.iloc[0] if not f.empty else "&ndash;"
            fs="%.2f"%f.net_sharpe.iloc[0] if not f.empty else "&ndash;"
            fcls=win(f.net_ann.iloc[0]) if not f.empty else ''
            h.append('<tr%s><td class="l b">%s</td><td class="l">%s</td><td>%.1f</td><td>%.1f</td><td%s>%.1f</td><td%s>%.2f</td><td%s>%s</td><td%s>%s</td><td>%.2f</td><td>%.1f</td></tr>'
                %(cls, L[m] if i==0 else "", p.replace("-","–"), c.gross_ann, c.cost_ann,
                  win(c.net_ann), c.net_ann, win(c.net_ann), c.net_sharpe, fcls, fn, fcls, fs,
                  c.t_gross, c.breakeven_bps))
    h.append('</tbody></table>'); return "".join(h)

def lag_table():
    d=bt[bt.variant.isin(["daily reversal","daily reversal, 1-day late"])&(bt.impl=="futures")]
    h=['<table class="t"><thead><tr><th class="l">Market</th><th class="l">Window</th><th>net % p.a.<br>trading at the close</th><th>net % p.a.<br>one day later</th><th>difference</th></tr></thead><tbody>']
    for m in ORDER:
        for p in MAIN_PERIODS:
            a=d[(d.mkt==m)&(d.period==p)&(d.variant=="daily reversal")]
            b=d[(d.mkt==m)&(d.period==p)&(d.variant=="daily reversal, 1-day late")]
            if a.empty or b.empty: continue
            x,y=a.net_ann.iloc[0],b.net_ann.iloc[0]
            h.append('<tr><td class="l">%s</td><td class="l">%s</td><td%s>%.1f</td><td%s>%.1f</td><td>%+.1f</td></tr>'
                     %(L[m],p.replace("-","–"),' class="win"' if x>0 else '',x,' class="win"' if y>0 else '',y,y-x))
    h.append('</tbody></table>'); return "".join(h)

HTML=f"""<!doctype html><html><head><meta charset="utf-8"><title>Does the pattern survive costs?</title>
<style>
@page {{ size:A4; margin:17mm 16mm 15mm; }}
body {{ font-family:"DejaVu Sans",Helvetica,sans-serif; color:#1c2530; font-size:10.3pt; line-height:1.56; margin:0; }}
h1 {{ font-size:20pt; line-height:1.15; margin:0 0 5px; letter-spacing:-.4px; }}
h2 {{ font-size:13pt; margin:22px 0 7px; color:#22303f; }}
h2 .n {{ color:#8b95a1; font-weight:400; margin-right:7px; }}
h3 {{ font-size:10.5pt; margin:15px 0 4px; color:#2f4b7c; }}
p {{ margin:0 0 9px; }}
.sub {{ color:#5a6673; font-size:10pt; margin:0 0 12px; }}
.rule {{ height:3px; background:#22303f; margin:11px 0 15px; }}
.tag {{ font-size:8.6pt; letter-spacing:.9px; text-transform:uppercase; color:#5a6673; margin-bottom:5px; }}
.big {{ background:#f6f8fa; border-left:4px solid #2f4b7c; padding:11px 14px; margin:13px 0 17px; }}
.big p {{ margin:0 0 8px; }} .big p:last-child {{ margin:0; }}
.warn {{ background:#fdf4f5; border-left:4px solid #d1495b; padding:11px 14px; margin:13px 0 17px; }}
.warn p:last-child {{ margin:0; }}
ul {{ margin:0 0 10px; padding-left:18px; }} li {{ margin-bottom:5px; }}
table.t {{ border-collapse:collapse; width:100%; font-size:7.9pt; margin:7px 0 4px; page-break-inside:avoid; }}
table.t th {{ background:#f1f4f7; border-top:1px solid #22303f; border-bottom:1px solid #b9c2cc; padding:4px; text-align:center; font-weight:600; }}
table.t td {{ padding:3.2px 4px; text-align:center; border-bottom:.5px solid #e6eaee; white-space:nowrap; }}
table.t th.l, table.t td.l {{ text-align:left; }}
table.t tbody tr:last-child td {{ border-bottom:1px solid #22303f; }}
td.win {{ background:#e4f1ec; font-weight:700; }}
th.tot, td.tot {{ background:#eef2f7; font-weight:700; }}
tr.grp td {{ border-top:.5px solid #b9c2cc; }}
td.b {{ font-weight:600; }}
.cap {{ font-size:8pt; color:#5a6673; margin:3px 0 14px; page-break-before:avoid; }}
.fig img {{ width:100%; }} .avoid {{ page-break-inside:avoid; }} .pb {{ page-break-before:always; }}
code {{ font-size:8.8pt; background:#f1f4f7; padding:0 3px; }}
</style></head><body>

<div class="tag">Addendum · transaction costs · Alpha Research Project</div>
<h1>Does the pattern survive trading costs?</h1>
<div class="sub">Follow-up to the variance ratio study. We take the one pattern the statistics found, try to actually trade it, and charge it every fee, spread, tax and borrow cost it would really pay. Prepared {datetime.date.today():%d %B %Y}.</div>
<div class="rule"></div>

<div class="big">
<p><b>1. Mostly no &mdash; but not entirely, and that is a change from what the first report said.</b> In the cheapest market in the world, the zig-zag trade did clear its costs. Betting against the S&amp;P 500's previous day, 2008&ndash;2012, made 24.4% a year before costs and <b>21.6% after</b> them. Costs took only 2.8 points because trading the S&amp;P is nearly free.</p>
<p><b>2. Everywhere else, costs destroy it, and taxes do most of the destroying.</b> The same trade in South African shares loses 71% a year after costs. In Indian shares, 53%. Not because the trade is worse &mdash; because South Africa charges 0.25% tax on every purchase and India charges 0.1% on both sides, and this strategy buys and sells every single day.</p>
<p><b>3. And the survivors die if you are one day late.</b> Execute the identical S&amp;P trade one day after the signal and 24.4% a year becomes 6.8%; in 2020&ndash;2021 it goes from +31.6% to &minus;27.2%. The entire edge lives inside one closing price. That is the finding that should stop you building this.</p>
</div>

<h2><span class="n">1</span>What we charged</h2>
<p>Four things are charged on every trade, plus a fifth for holding a short position:</p>
<ul>
<li><b>Half the bid&ndash;ask spread</b> &mdash; you buy at the ask and sell at the bid, so crossing once costs half the gap.</li>
<li><b>Commission</b> &mdash; what the broker takes.</li>
<li><b>Exchange and clearing fees</b> &mdash; the venue's cut.</li>
<li><b>Transaction taxes</b> &mdash; the government's cut, and the one that decides this whole question.</li>
<li><b>Stock borrow</b> &mdash; to bet against a market you must borrow the shares and pay a fee for every day you hold them short.</li>
</ul>
{cost_table()}
<div class="cap">Table 1 &mdash; Cost assumptions, one-way, in basis points (1 bp = 0.01%). <b>Tax figures are statutory and sourced:</b> South Africa's Securities Transfer Tax is 0.25% on purchases of listed shares (<a href="https://www.sars.gov.za/types-of-tax/securities-transfer-tax/">SARS</a>); India's STT is 0.10% on both sides of delivery trades and 0.05% on the sell side of index futures (<a href="https://www.vrdnation.com/stt-cash-fno-intraday/">rates effective 2026</a>); Brazil's B3 charges 0.030% per side in exchange and settlement fees (<a href="https://blog.nelogica.com.br/emolumentos/">B3 tariff schedule</a>); the US levies no transaction tax. Spreads, commissions and borrow rates are assumptions for a small institutional account &mdash; which is why every result below is also given as a <i>breakeven</i> cost that depends on no assumption at all. Index futures escape the share-transfer taxes entirely, which is why the futures column exists. There is no futures market on African equities outside South Africa, which is itself part of the answer.</div>

<h2><span class="n">2</span>The trade we tested</h2>
<p>A variance ratio below 1 says a market zig-zags: part of each move gets taken back. The trade that implies is simple and unglamorous &mdash; <b>bet against the last move</b>. If yesterday was up, go short today. If yesterday was down, go long. Full position, every day, no filters, no stop losses, no optimisation. We also ran a slower version that uses the past week and only rebalances weekly, because trading less often is the obvious defence against costs.</p>
<p>Both versions assume you trade at the closing price that produced the signal &mdash; the most favourable assumption available. Section 5 is about what happens when you cannot.</p>

<h2><span class="n">3</span>What happened</h2>
{results_table("daily reversal")}
<div class="cap">Table 2 &mdash; The daily reversal trade. Green = made money after costs. "Breakeven" is the cost per leg at which the trade earns exactly zero: compare it to the all-in cost in Table 1. The t-stat is on the gross profit &mdash; below about 2 the result is weak enough to be luck.</div>

<div class="fig avoid"><img src="{img('cost_waterfall.png')}"></div>
<div class="cap">Figure 1 &mdash; Gross profit, costs and what is left, for the daily trade in cash shares. In South Africa, Africa and India the red bar is several times the grey one. The trade is not bad in those markets; it is simply unaffordable.</div>

<h3>Two combinations survived</h3>
<p><b>The S&amp;P 500 in 2008&ndash;2012</b> is the headline: 24.4% gross, 21.6% net, a Sharpe ratio of 0.82 after costs, against a market that returned &minus;0.3% a year over the same stretch. The trade was right on 51.0% of days &mdash; that is the entire edge, a coin that lands your way 51 times in 100, repeated 1,258 times.</p>
<p><b>The Ibovespa in 2020&ndash;2021</b> also cleared: 55.4% gross, 29.0% net in cash and 44.1% through futures, breakeven 19.6 bps against 9.0 charged. Note that the variance ratio test did <i>not</i> flag Brazil as significant in that window. The trade made money on the few violent covid days while the statistical test, which is built to discount wild days, correctly refused to call it a pattern. One of the two is wrong, and over two years of data it is not obvious which.</p>

<h3>Taxes are the whole story elsewhere</h3>
<p>A trade that flips position every day turns over roughly <b>250 times its own size per year</b>. That multiplier is what makes small costs lethal: at South Africa's 26 bps all-in, 250 &times; 26 bps = 65% a year in costs. The arithmetic is not subtle, and no amount of signal quality survives it.</p>
<p>Trading index futures instead of shares removes the transfer taxes and roughly quarters the cost in South Africa and India &mdash; from &minus;72% to &minus;18% a year in South Africa. Better, still losing. The slower weekly version helps more, because it trades a fifth as often, and it turns three combinations mildly positive (South Africa and India via futures). But their t-stats are 1.1 to 1.3, which is the statistical signature of noise.</p>

<div class="fig avoid"><img src="{img('cost_sweep.png')}"></div>
<div class="cap">Figure 2 &mdash; The same result without any cost assumption. Each line shows what the trade nets as costs rise; where it crosses zero is that market's true breakeven. The dot is what that market actually charges. Only the S&amp;P 500's dot (and Brazil's, in 2020&ndash;2021) sits to the left of its crossing point.</div>

<h2><span class="n">4</span>So the first report was wrong?</h2>
<p>Partly, and it is worth being exact about it. The earlier report said the one statistically significant finding was "not tradeable", and justified that with transaction costs in the abstract. Having now actually charged those costs, that claim was too strong: in the S&amp;P 500, the cheapest market there is, the trade clears its costs with room to spare &mdash; it needs costs below 9.5 bps per leg and pays about 1.0.</p>
<p>What the first report got right is the conclusion, for different reasons. The trade is fragile in ways that have nothing to do with fees, and section 5 is the demonstration.</p>

<h2><span class="n">5</span>The test that actually kills it</h2>
<p>Everything above assumes you trade at the exact closing price that generates your signal. Real money cannot always do that: you are competing with every other closing-auction order, and in size you move the price you are trying to trade at. So we reran it with a one-day delay &mdash; same signal, same costs, just acted on a day later.</p>
{lag_table()}
<div class="cap">Table 3 &mdash; Net return trading at the close versus one day later, futures implementation (the cheapest, so the comparison is about timing and not fees).</div>

<div class="fig avoid"><img src="{img('equity_spx_0812.png')}"></div>
<div class="cap">Figure 3 &mdash; $100 in the best case in the whole study. Costs cost you something (dark blue below pale blue) but do not break the trade. Being one day late (red) does. That gap is not a fee &mdash; it is the edge itself, and it lasts less than 24 hours.</div>

<div class="warn">
<p><b>Read figure 3 as the conclusion.</b> An edge that exists at the close and is gone by the next one is not a strategy a person can run. It is a statement about how fast prices absorbed information during a panic &mdash; which is interesting, and is the thing worth studying &mdash; but turning it into money would mean competing for the closing print against people whose entire business is competing for the closing print.</p>
</div>

<h2><span class="n">6</span>The weekly version, for completeness</h2>
{results_table("weekly reversal")}
<div class="cap">Table 4 &mdash; The weekly reversal trade, which trades a fifth as often. Cheaper, and that is enough to rescue a few combinations &mdash; but none with a t-stat near 2, and the S&amp;P's covid-window version loses 21% a year. Trading less often does not create an edge; it only stops costs eating one that is already there.</div>

<h2><span class="n">7</span>What would have to be true to believe this</h2>
<ul>
<li><b>Execution at the close, at size, during a panic.</b> Figure 3 says this is the whole ballgame. You would need to measure your real fill prices in 2008-style conditions, not assume them.</li>
<li><b>A better t-stat.</b> 2.07 over five years is a two-sigma result, and we went looking for it <i>after</i> the variance ratio test pointed at that market and that period. Honest discovery costs you significance.</li>
<li><b>Survival out of sample.</b> It half-survives: the S&amp;P trade still worked in 2020&ndash;2021 (t = 1.71) and is gone by 2022&ndash;2026 (t = 0.88, net 4.3%). A pattern that only pays during crises is a bet on the next crisis, not an edge.</li>
<li><b>Capacity.</b> None of this models market impact. At $1m it is a rounding error; at $100m, trading 250&times; turnover a year into closing auctions, it is the dominant cost and it is not in any table here.</li>
</ul>

<h2><span class="n">8</span>How to reproduce or change the assumptions</h2>
<p>Every cost in Table 1 lives in one file, <code>src/costs.py</code>, as plain numbers with sources in the docstring. Change them, rerun <code>python src/backtest.py</code>, and every table and figure here regenerates. If you think the Africa ETF's spread is 15 bps rather than 25, or that your broker charges less, you can see the answer in a few seconds &mdash; and the breakeven column tells you in advance which way it will go.</p>
</body></html>"""
out=os.path.join(ROOT,"reports","transaction_costs.html")
open(out,"w").write(HTML); print("wrote",out)
