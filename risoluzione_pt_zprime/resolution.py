import ROOT

N_SIGMA_FIT = 2.0
MAX_ITER = 5
CONV_TOL = 1e-3
MIN_ENTRIES_GAUS = 50
# Le code oltre la finestra non falsano il fit del core, che lavora entro
# +-2 sigma dal picco: la soglia serve solo a scartare i casi in cui la
# finestra e' cosi' stretta da tagliare il core stesso.
MAX_OUTFLOW_FRAC = 0.10


def outflow_fraction(h):
    n_in = h.Integral()
    n_under = h.GetBinContent(0)
    n_over = h.GetBinContent(h.GetNbinsX() + 1)
    n_tot = n_in + n_under + n_over
    if n_tot <= 0:
        return 1.0
    return (n_under + n_over) / n_tot


def extract_sigma(h):
    entries = h.GetEntries()
    out = {
        "sigma": None, "sigma_err": None, "mu": None, "mu_err": None,
        "outflow": outflow_fraction(h), "entries": entries,
        "ok": False, "reason": "",
    }

    if entries < MIN_ENTRIES_GAUS:
        out["reason"] = f"solo {entries:.0f} entries (< {MIN_ENTRIES_GAUS})"
        return out

    if out["outflow"] > MAX_OUTFLOW_FRAC:
        out["reason"] = (f"{100*out['outflow']:.1f}% degli eventi in "
                         f"over/underflow: finestra troppo stretta")
        return out

    mu = h.GetMean()
    sg = h.GetRMS()
    if sg <= 0:
        out["reason"] = "RMS nullo"
        return out

    best = None
    for it in range(MAX_ITER):
        lo = mu - N_SIGMA_FIT * sg
        hi = mu + N_SIGMA_FIT * sg
        f = ROOT.TF1(f"gaus_{h.GetName()}_{it}", "gaus", lo, hi)
        f.SetParameters(h.GetMaximum(), mu, sg)

        res = h.Fit(f, "QRNS")
        if not res.Get() or not res.IsValid():
            break

        mu_new = f.GetParameter(1)
        sg_new = f.GetParameter(2)
        if sg_new <= 0:
            break

        converged = abs(sg_new - sg) / sg < CONV_TOL
        mu, sg = mu_new, sg_new
        best = (f.GetParameter(2), f.GetParError(2),
                f.GetParameter(1), f.GetParError(1))
        if converged:
            break

    if best is None:
        out["reason"] = "fit gaussiano non convergente"
        return out

    out["sigma"], out["sigma_err"], out["mu"], out["mu_err"] = best
    if out["sigma_err"] <= 0:
        out["reason"] = "errore sulla sigma nullo"
        return out

    out["ok"] = True
    return out
