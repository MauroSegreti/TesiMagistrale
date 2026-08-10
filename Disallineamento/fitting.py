import array
import ROOT
from config import PT_BINS, ETA_BINS, MIN_ENTRIES_FOR_FIT, MIN_REL_ERR
from resolution import extract_width
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
    f = ROOT.TF1(name, FIT_FORMULA, x_lo, x_hi)
    f.SetParameters(r0_seed, r1_seed, r2_seed)
    f.SetParNames("r0", "r1", "r2")
    f.SetParLimits(0, 0, 50)
    f.SetParLimits(1, 0, 1)
    f.SetParLimits(2, 0, 1)
    if fix_r0:
        f.FixParameter(0, 0)
    return f


def _fit_multistart(graph, name_prefix, color, fix_r0, x_lo, x_hi):
    best_fit = None
    best_chi2ndf = float("inf")
    best_res = None
    attempts = []
    last_fit = last_res = None

    for i, seed in enumerate(_SEEDS):
        f = _make_fit(f"{name_prefix}_try{i}", seed, fix_r0, x_lo, x_hi)
        res = graph.Fit(f, "QRNS EX0")
        last_fit, last_res = f, res

        valid = bool(res.Get()) and res.IsValid()
        ndf = f.GetNDF()
        chi2ndf = f.GetChisquare() / ndf if ndf > 0 else float("inf")
        attempts.append((chi2ndf, valid))

        if valid and chi2ndf < best_chi2ndf:
            best_chi2ndf, best_fit, best_res = chi2ndf, f, res

    if best_fit is None:
        print(f"       [WARNING] nessun seed convergiuto per {name_prefix}")
        best_fit, best_res = last_fit, last_res

    best_fit.SetLineColor(color)
    best_fit.SetLineWidth(2)
    return best_fit, attempts, best_res


def _print_correlation(res):
    if res is None or not res.Get():
        return
    try:
        corr = res.Correlation(0, 1)
        flag = "  <-- degenere" if abs(corr) > 0.9 else ""
        print(f"       corr(r0, r1) = {corr:+.3f}{flag}")
    except Exception:
        pass


def build_graphs_and_fits(histos, pt_sums=None, pt_counts=None,
                          method="q68", pt_max=None, fit_pt_max=None,
                          verbose=True):
    """
    method : 'q68' (default, indicazione di Luca) oppure 'gaus'
    pt_max : se dato, scarta i punti con pT medio effettivo superiore
             (li toglie anche dal grafico: usato per la sistematica sul
             range, dove il confronto e' "se non fossimo andati cosi'
             in alto")
    fit_pt_max : se dato, i punti restano nel grafico (misure valide)
             ma il fit usa solo quelli con pT <= fit_pt_max. La curva
             viene comunque disegnata estrapolata su tutto il range, per
             mostrare dove la formula smette di descrivere i dati.
    """
    graphs = []

    for e_i, e in enumerate(ETA_BINS):
        x = array.array('d')
        y = array.array('d')
        ex = array.array('d')
        ey = array.array('d')

        skipped = []
        points = []

        for p_i, p in enumerate(PT_BINS):
            h = histos[e_i][p_i]

            if h.GetEntries() < MIN_ENTRIES_FOR_FIT:
                skipped.append((p["name"], f"{h.GetEntries():.0f} entries"))
                continue

            info = extract_width(h, method=method)
            if not info["ok"]:
                skipped.append((p["name"], info["reason"]))
                continue

            if pt_sums is not None and pt_counts[e_i][p_i] > 0:
                x_val = pt_sums[e_i][p_i] / pt_counts[e_i][p_i]
            else:
                x_val = p["mean"]

            if pt_max is not None and x_val > pt_max:
                skipped.append((p["name"],
                                f"pT medio {x_val:.0f} > {pt_max:.0f} GeV"))
                continue

            # floor sistematico: non pretendiamo dalla formula una
            # precisione migliore di MIN_REL_ERR, vedi config.py
            err = max(info["sigma_err"], MIN_REL_ERR * info["sigma"])

            x.append(x_val)
            ex.append(0.0)
            y.append(info["sigma"])
            ey.append(err)
            points.append({"pt": x_val, "name": p["name"], **info})

        if verbose and skipped:
            print(f"\n[INFO] eta bin {e_i} ({e['label']}) -- bin scartati:")
            for name, reason in skipped:
                print(f"         {name}: {reason}")

        if len(x) < 3:
            print(f"[WARNING] solo {len(x)} punti validi per eta bin {e_i} "
                  f"({e['label']}), salto")
            continue

        n_points = len(x)
        x_lo, x_hi = min(x) * 0.9, max(x) * 1.1
        fit_hi = x_hi if fit_pt_max is None else min(x_hi, fit_pt_max)

        color = PALETTE[e_i % len(PALETTE)]
        g = ROOT.TGraphErrors(n_points, x, y, ex, ey)
        g.SetName(f"g_eta_{e_i}_{method}")
        g.SetLineColor(color)
        g.SetMarkerColor(color)
        g.SetMarkerStyle(20)
        g.SetLineWidth(2)

        if verbose:
            print(f"\n[INFO] Fit eta bin {e_i} ({e['label']}) -- {n_points} "
                  f"punti, pT in [{min(x):.0f}, {max(x):.0f}] GeV, "
                  f"stimatore '{method}'")

        fit_free, att_free, res_free = _fit_multistart(
            g, f"fit_eta_{e_i}_{method}_free", color, False, x_lo, fit_hi)
        fit_fix0, att_fix0, res_fix0 = _fit_multistart(
            g, f"fit_eta_{e_i}_{method}_fix0", color, True, x_lo, fit_hi)

        if verbose:
            print(f"       r0 libero  chi2/ndf: "
                  f"{['%.2f' % v if ok else 'FAIL' for v, ok in att_free][0]}")
            _print_correlation(res_free)
            print(f"       r0 = 0     chi2/ndf: "
                  f"{['%.2f' % v if ok else 'FAIL' for v, ok in att_fix0][0]}")

        graphs.append({
            "graph": g,
            "fit": fit_free,
            "fit_fixed0": fit_fix0,
            "eta": e,
            "eta_index": e_i,
            "n_points": n_points,
            "x_lo": x_lo,
            "x_hi": x_hi,
            "method": method,
            "points": points,
        })

    return graphs
