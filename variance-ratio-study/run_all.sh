#!/usr/bin/env bash
# Reproduce the whole study from scratch.
set -euo pipefail
cd "$(dirname "$0")"

echo "== validating the variance ratio implementation"
python3 - <<'PY'
import sys, numpy as np
sys.path.insert(0, "src")
from vrtest import vr_stats
rng = np.random.default_rng(1)
# size under an i.i.d. random walk
rej = sum(abs(vr_stats(np.concatenate([[0], np.cumsum(rng.standard_normal(1500)*0.01)]), 5)['z2']) > 1.96
          for _ in range(300)) / 300
# AR(1) recovery against theory
rho = 0.2; r = np.zeros(4000); e = rng.standard_normal(4000)*0.01
for t in range(1, 4000): r[t] = rho*r[t-1] + e[t]
x = np.concatenate([[0], np.cumsum(r)])
est = {q: round(vr_stats(x, q)['vr'], 2) for q in (2, 5, 10, 20)}
th = {q: round(1 + 2*sum((1-j/q)*rho**j for j in range(1, q)), 2) for q in (2, 5, 10, 20)}
print(f"   empirical size of z2 at 5%: {rej:.3f}  (expect ~0.05-0.07)")
print(f"   AR(1) VR estimated {est}")
print(f"   AR(1) VR theory    {th}")
assert rej < 0.12, "size is out of line - check the implementation"
PY

echo "== fetching data";        python3 src/fetch_data.py
echo "== study 1: variance ratios"; python3 src/run_vr.py
echo "== study 2: costs";       python3 src/backtest.py | tail -5
echo "== figures";              python3 src/make_figures.py
echo "== report";               python3 src/build_report.py
CHROME=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1 || true)
if [ -n "$CHROME" ]; then
  "$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
    --print-to-pdf="$PWD/reports/Transaction_Costs_Addendum.pdf" \
    "file://$PWD/reports/transaction_costs.html" 2>/dev/null
  echo "   PDF written"
else
  echo "   no chromium found - reports/transaction_costs.html is ready to print"
fi
echo "done."
