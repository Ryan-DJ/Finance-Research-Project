"""Transaction cost assumptions, one-way, in basis points of traded notional.

Statutory items are sourced; execution items (spread, commission, impact) are
assumptions for a small institutional account trading liquid index exposure.
Because the execution items are assumptions, every result is accompanied by a
BREAKEVEN cost, which depends on no assumption at all.

Sources for statutory items
  South Africa  Securities Transfer Tax 0.25% on the PURCHASE of listed shares.
                SARS: https://www.sars.gov.za/types-of-tax/securities-transfer-tax/
                Not levied on index futures (no transfer of a security).
  India         STT 0.10% on BOTH sides of delivery-based equity trades;
                0.025% on the SELL side of intraday equity; 0.05% on the SELL
                side of equity futures (rates effective 2026).
                https://www.vrdnation.com/stt-cash-fno-intraday/
  Brazil        B3 exchange + settlement fees total 0.030% per side for normal
                (overnight) operations, 0.023% for day trade.
                https://blog.nelogica.com.br/emolumentos/
  USA           No transaction tax; SEC Section 31 fee applies to sells only
                and is immaterial at ~0.2 bp.
"""

# half_spread: half the quoted bid-ask, i.e. the cost of crossing once
# commission:  broker commission per side
# fees:        exchange / clearing / regulatory, per side
# tax_buy / tax_sell: statutory transaction taxes, per side
# borrow:      annualised stock-borrow fee, charged only on days held short
CASH = {
    "SPX":   dict(half_spread=0.5, commission=0.3, fees=0.2, tax_buy=0.0,  tax_sell=0.0,  borrow=50),
    "JSE40": dict(half_spread=8.0, commission=5.0, fees=0.5, tax_buy=25.0, tax_sell=0.0,  borrow=150),
    "AFK":   dict(half_spread=25.0,commission=0.5, fees=0.2, tax_buy=0.0,  tax_sell=0.0,  borrow=400),
    "IBOV":  dict(half_spread=4.0, commission=2.0, fees=3.0, tax_buy=0.0,  tax_sell=0.0,  borrow=200),
    "NIFTY": dict(half_spread=3.0, commission=2.0, fees=0.3, tax_buy=10.0, tax_sell=10.0, borrow=150),
}
# Index futures: no transfer taxes (except Indian STT on the sell side), tighter
# spreads, no borrow cost. AFK has no futures market at all.
FUTURES = {
    "SPX":   dict(half_spread=0.3, commission=0.2, fees=0.05, tax_buy=0.0, tax_sell=0.0, borrow=0),
    "JSE40": dict(half_spread=3.0, commission=2.0, fees=0.5,  tax_buy=0.0, tax_sell=0.0, borrow=0),
    "AFK":   None,
    "IBOV":  dict(half_spread=2.0, commission=1.0, fees=1.0,  tax_buy=0.0, tax_sell=0.0, borrow=0),
    "NIFTY": dict(half_spread=1.5, commission=1.0, fees=0.3,  tax_buy=0.0, tax_sell=5.0, borrow=0),
}

def one_way(c, side):
    """Total one-way cost in bps for a buy or a sell."""
    if c is None: return None
    return c["half_spread"] + c["commission"] + c["fees"] + (c["tax_buy"] if side == "buy" else c["tax_sell"])

def round_trip(c):
    if c is None: return None
    return one_way(c, "buy") + one_way(c, "sell")
