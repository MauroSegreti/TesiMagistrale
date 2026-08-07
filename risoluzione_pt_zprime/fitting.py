import array
import ROOT
from config import PT_BINS, ETA_BINS, MIN_ENTRIES_FOR_FIT
from resolution import extract_sigma
from style import PALETTE

FIT_FORMULA = "sqrt(([0]/x)*([0]/x) + [1]*[1] + ([2]*x)*([2]*x))"

_SEEDS = [
    (0.1, 0.025, 0.0001),
    (1.0, 0.030, 0.0001),
    (3.0, 0.020, 0.0002),
    (0.01, 0.035, 0.0005),
    (5.0, 0.028, 0.00005),
    (0.5, 0.022, 0.00015),
]


def _make_fit(name, seed, fix_r0, x_lo, x_hi):
    r0_seed, r1_seed, r2_seed = seed
    fit_func = ROOT.TF1(name, FIT_FORMULA, x_lo, x_hi)
    fit_func.SetParameters(r0_seed, r1_seed, r2_seed)
    fit_func.SetParNames("r0", "r1", "r2")
    fit_func.SetParLimits(0, 0, 50)
    fit_func.SetParLimits(1, 0, 1)
    fit_func.SetParLimits(2, 0, 1)
    if fix_r0:
        fit_func.FixParameter(0, 0)
    return fit_func


def _fit_multistart(graph, name_prefix, color, fix_r0, x_lo, x_hi):
    best_fit = None
    best_chi2ndf = float("inf")
    best_res = None
    attempts = []
    last_fit = None
    last_res = None

    for i, seed in enumerate(_SEEDS):
        fit_func = _make_fit(f"{name_prefix}_try{i}", seed, fix_r0, x_lo, x_hi)
        res = graph.Fit(fit_func, "QRNS EX0")
        last_fit, last_res = fit_func, res

        valid = bool(res.Get()) and res.IsValid()
        ndf = fit_func.GetNDF()
        chi2 = fit_func.GetChisquare()
        chi2ndf = chi2 / ndf if ndf > 0 else float("inf")
        attempts.append((chi2ndf, valid))

        if valid and chi2ndf < best_chi2ndf:
            best_chi2ndf = chi2ndf
            best_fit = fit_func
            best_res = res

    if best_fit is None:
        print(f"       [WARNING] Nessun seed convergiuto per {name_prefix}, "
              f"uso l'ultimo tentativo")
        best_fit = last_fit
        best_res = last_res

    best_fit.SetLineColor(color)
    best_fit.SetLineWidth(2)
    return best_fit, attempts, best_res


def _print_correlation(res, fix_r0):
    if fix_r0 or res is None or not res.Get():
        return
    try:
        corr = res.Correlation(0, 1)
        flag = "  <-- DEGENERE" if abs(corr) > 0.9 else ""
        print(f"       corr(r0, r1) = {corr:+.3f}{flag}")
    except Exception:
        pass


def build_graphs_and_fits(histos, pt_sums=None, pt_counts=None, pt_max=None):
    """pt_max: se dato, scarta i punti il cui pT medio effettivo lo supera."""
    graphs = []

    for e_i, e in enumerate(ETA_BINS):
        x = array.array('d')
        y = array.array('d')
        ex = array.array('d')
        ey = array.array('d')

        skipped = []

        for p_i, p in enumerate(PT_BINS):
            h = histos[e_i][p_i]

            if h.GetEntries() < MIN_ENTRIES_FOR_FIT:
                skipped.append((p["name"], f"{h.GetEntries():.0f} entries"))
                continue

            info = extract_sigma(h)
            if not info["ok"]:
                skipped.append((p["name"], info["reason"]))
                continue

            if pt_sums is not None and pt_counts[e_i][p_i] > 0:
                x_val = pt_sums[e_i][p_i] / pt_counts[e_i][p_i]
            else:
                x_val = p["mean"]

            if pt_max is not None and x_val > pt_max:
                skipped.append((p["name"], f"pT medio {x_val:.0f} > {pt_max:.0f} GeV"))
                continue

            x.append(x_val)
            ex.append(0.0)
            y.append(info["sigma"])
            ey.append(info["sigma_err"])

        if skipped:
            print(f"\n[INFO] eta bin {e_i} ({e['label']}) -- bin di pT scartati:")
            for name, reason in skipped:
                print(f"         {name}: {reason}")

        if len(x) < 3:
            print(f"[WARNING] Solo {len(x)} punti validi per eta bin {e_i} "
                  f"({e['label']}), salto")
            continue

        n_points = len(x)
        x_lo = min(x) * 0.9
        x_hi = max(x) * 1.1

        color = PALETTE[e_i % len(PALETTE)]
        g = ROOT.TGraphErrors(n_points, x, y, ex, ey)
        g.SetName(f"g_eta_{e_i}")
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.SetMarkerStyle(20)
        g.SetLineWidth(2)

        print(f"\n[INFO] Fit eta bin {e_i} ({e['label']}) -- {n_points} punti, "
              f"pT in [{min(x):.0f}, {max(x):.0f}] GeV")

        print("       r0 libero:")
        fit_free, att_free, res_free = _fit_multistart(
            g, f"fit_eta_{e_i}_free", color, False, x_lo, x_hi)
        print(f"       chi2/ndf per seed: "
              f"{[('%.2f' % v if ok else 'FAIL') for v, ok in att_free]}")
        _print_correlation(res_free, False)

        print("       r0 fissato a 0:")
        fit_fixed0, att_fix0, res_fix0 = _fit_multistart(
            g, f"fit_eta_{e_i}_fix0", color, True, x_lo, x_hi)
        print(f"       chi2/ndf per seed: "
              f"{[('%.2f' % v if ok else 'FAIL') for v, ok in att_fix0]}")

        graphs.append({
            "graph": g,
            "fit": fit_free,
            "fit_fixed0": fit_fixed0,
            "eta": e,
            "n_points": n_points,
            "x_lo": x_lo,
            "x_hi": x_hi,
        })

    return graphs
