"""
Estrazione della larghezza della distribuzione di risoluzione.

Due stimatori:

  q68    semi-ampiezza dell'intervallo centrale al 68%, (q84 - q16)/2.
         Non assume nessuna forma: e' il metodo indicato da Luca.
         Errore: sigma / sqrt(2N).

  gaus   fit gaussiano iterativo entro +-2 sigma dal core.
         Tenuto come confronto: la differenza con q68 e' la sistematica
         sul metodo.

Riporta anche l'asimmetria, che dice quanto la distribuzione si discosta
dalla gaussiana:
    asym = [(q84 - mediana) - (mediana - q16)] / (q84 - q16)
0 = simmetrica; |asym| > 0.1 = coda marcata da un lato.
"""

import math
import array

import ROOT

N_SIGMA_FIT = 2.0
MAX_ITER = 5
CONV_TOL = 1e-3

MIN_ENTRIES = 200
# q68 usa solo il 68% centrale, quindi tollera code fuori finestra molto
# meglio di un fit: la soglia serve solo a scartare i casi patologici.
MAX_OUTFLOW_FRAC = 0.15


def outflow_fraction(h):
    n_in = h.Integral()
    n_out = h.GetBinContent(0) + h.GetBinContent(h.GetNbinsX() + 1)
    tot = n_in + n_out
    return n_out / tot if tot > 0 else 1.0


def _quantiles(h, probs):
    q = array.array('d', [0.0] * len(probs))
    p = array.array('d', probs)
    n = h.GetQuantiles(len(probs), q, p)
    if n < len(probs):
        return None
    return list(q)


def sigma_q68(h):
    """(q84 - q16) / 2, errore sigma/sqrt(2N)."""
    qs = _quantiles(h, [0.16, 0.50, 0.84])
    if qs is None:
        return None
    q16, med, q84 = qs
    s = (q84 - q16) / 2.0
    if s <= 0:
        return None
    n = h.GetEntries()
    span = q84 - q16
    asym = ((q84 - med) - (med - q16)) / span if span > 0 else 0.0
    return {
        "sigma": s,
        "sigma_err": s / math.sqrt(2.0 * n) if n > 0 else None,
        "mu": med,
        "q16": q16,
        "q84": q84,
        "asym": asym,
    }


def sigma_gaus(h, n_sigma=N_SIGMA_FIT):
    """Fit gaussiano iterativo entro +-n_sigma dal core."""
    mu = h.GetMean()
    sg = h.GetRMS()
    if sg <= 0:
        return None

    best = None
    for it in range(MAX_ITER):
        f = ROOT.TF1(f"gaus_{h.GetName()}_{n_sigma}_{it}", "gaus",
                     mu - n_sigma * sg, mu + n_sigma * sg)
        f.SetParameters(h.GetMaximum(), mu, sg)
        res = h.Fit(f, "QRNS")
        if not res.Get() or not res.IsValid():
            break
        mu_new, sg_new = f.GetParameter(1), f.GetParameter(2)
        if sg_new <= 0:
            break
        converged = abs(sg_new - sg) / sg < CONV_TOL
        mu, sg = mu_new, sg_new
        best = {
            "sigma": f.GetParameter(2), "sigma_err": f.GetParError(2),
            "mu": f.GetParameter(1), "mu_err": f.GetParError(1),
        }
        if converged:
            break
    return best


def extract_width(h, method="q68"):
    """
    Ritorna sempre un dict; il chiamante filtra su 'ok'.
    Chiavi: sigma, sigma_err, mu, asym, entries, outflow, ok, reason,
            e sigma_q68 / sigma_gaus per il confronto fra metodi.
    """
    entries = h.GetEntries()
    out = {
        "sigma": None, "sigma_err": None, "mu": None, "asym": None,
        "entries": entries, "outflow": outflow_fraction(h),
        "sigma_q68": None, "sigma_gaus": None,
        "ok": False, "reason": "",
    }

    if entries < MIN_ENTRIES:
        out["reason"] = f"solo {entries:.0f} entries (< {MIN_ENTRIES})"
        return out

    if out["outflow"] > MAX_OUTFLOW_FRAC:
        out["reason"] = (f"{100*out['outflow']:.1f}% degli eventi in "
                         f"over/underflow: finestra troppo stretta")
        return out

    q = sigma_q68(h)
    g = sigma_gaus(h)
    out["sigma_q68"] = q["sigma"] if q else None
    out["sigma_gaus"] = g["sigma"] if g else None
    if q:
        out["asym"] = q["asym"]

    chosen = q if method == "q68" else g
    if chosen is None:
        out["reason"] = f"stimatore '{method}' non calcolabile"
        return out

    out["sigma"] = chosen["sigma"]
    out["sigma_err"] = chosen["sigma_err"]
    out["mu"] = chosen["mu"]

    if not out["sigma_err"] or out["sigma_err"] <= 0:
        out["reason"] = "errore sulla sigma nullo"
        return out

    out["ok"] = True
    return out
