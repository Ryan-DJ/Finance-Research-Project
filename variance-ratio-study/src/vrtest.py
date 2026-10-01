"""Lo-MacKinlay (1988) variance ratio tests, Chow-Denning (1993) joint test,
and Kim (2006) wild bootstrap p-values."""
import numpy as np
from math import sqrt
from scipy.stats import norm

def vr_stats(x, q):
    """x: log price levels. Lo-MacKinlay unbiased overlapping estimator."""
    x = np.asarray(x, dtype=float)
    n = len(x) - 1
    if n < q * 2:
        return None
    mu = (x[-1] - x[0]) / n
    r = np.diff(x) - mu
    sig_a = np.sum(r ** 2) / (n - 1)
    m = q * (n - q + 1) * (1.0 - q / n)
    dq = x[q:] - x[:-q] - q * mu
    sig_c = np.sum(dq ** 2) / m
    vr = sig_c / sig_a
    phi = 2.0 * (2 * q - 1) * (q - 1) / (3.0 * q * n)
    z1 = (vr - 1.0) / sqrt(phi)
    r2 = r ** 2
    denom = np.sum(r2) ** 2
    phi_star = 0.0
    for j in range(1, q):
        delta = np.sum(r2[j:] * r2[:-j]) / denom
        phi_star += ((2.0 * (q - j) / q) ** 2) * delta
    z2 = (vr - 1.0) / sqrt(phi_star)
    return dict(q=q, n=n, vr=vr, z1=z1, z2=z2,
                p1=2 * (1 - norm.cdf(abs(z1))), p2=2 * (1 - norm.cdf(abs(z2))))

def chow_denning(x, qs):
    zs = [vr_stats(x, q)['z2'] for q in qs]
    mv = max(abs(z) for z in zs)
    return mv, 1.0 - (2 * norm.cdf(mv) - 1) ** len(qs), zs

def wild_bootstrap(ret, qs, nboot=2000, seed=7, kind="mammen"):
    rng = np.random.default_rng(seed)
    n = len(ret)
    x0 = np.concatenate([[0.0], np.cumsum(ret)])
    obs = {q: vr_stats(x0, q)['z2'] for q in qs}
    obs_mv = max(abs(v) for v in obs.values())
    cnt = {q: 0 for q in qs}; cnt_mv = 0
    a, b = (1 - sqrt(5)) / 2, (1 + sqrt(5)) / 2
    pa = (sqrt(5) + 1) / (2 * sqrt(5))
    for _ in range(nboot):
        eta = np.where(rng.random(n) < pa, a, b) if kind == "mammen" else rng.standard_normal(n)
        xb = np.concatenate([[0.0], np.cumsum(eta * ret)])
        mvb = 0.0
        for q in qs:
            zb = vr_stats(xb, q)['z2']
            if abs(zb) >= abs(obs[q]): cnt[q] += 1
            mvb = max(mvb, abs(zb))
        if mvb >= obs_mv: cnt_mv += 1
    return {q: (cnt[q] + 1) / (nboot + 1) for q in qs}, (cnt_mv + 1) / (nboot + 1)
