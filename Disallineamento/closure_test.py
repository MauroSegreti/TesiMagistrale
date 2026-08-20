"""
Closure test dei fit: stessa regione di |eta|, confronto r0/r1/r2 fra
nominale (PerfectAlignment, Allineamento/) e misaligned (Disallineamento/).

Il test si aspetta r0 (multiple scattering) e r1 (risoluzione intrinseca)
compatibili fra i due campioni, mentre r2 (alta pT) cambia per via del
disallineamento. Le celle di r0/r1 dove la differenza supera 2 sigma
combinate vengono evidenziate in rosso.

Uso (da Disallineamento/, dopo aver girato analyze.py in entrambe le
cartelle cosi' esistono i due merged_res.root):
    python3 closure_test.py
"""

import os
import math

import ROOT

from config import PT_FIT_MAX
from compare_alignment import load, NOMINAL_ROOT, MISALIGNED_ROOT
from fitting import build_graphs_and_fits
import style

style.apply_style()

ANADIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ANADIR, "images")

_HEADER_HEX = "#16213e"
_ZEBRA_HEX = "#f0f0f5"
_BAD_HEX = "#8b1e1e"
_header_color = ROOT.TColor.GetColor(_HEADER_HEX)
_zebra_color = ROOT.TColor.GetColor(_ZEBRA_HEX)
_bad_color = ROOT.TColor.GetColor(_BAD_HEX)

_N_SIGMA_WARN = 2.0

# leading edge + 9 equal-width value columns (3 params x [nominal, misaligned, delta])
_X0, _X1 = 0.02, 0.98
_REGION_W = 0.11
_VALUE_W = (_X1 - _X0 - _REGION_W) / 9.0
_COL_EDGES = [_X0, _X0 + _REGION_W] + \
             [_X0 + _REGION_W + i * _VALUE_W for i in range(1, 10)]
_GROUPS = [("r_{0} [GeV]", 1, 4), ("r_{1}", 4, 7),
           ("r_{2} [GeV^{-1}] (#times10^{-3})", 7, 10)]
_SUBCOLS = ["Nominal", "Misaligned", "#Delta"] * 3
# only the boundaries *between* groups (Region|r0, r0|r1, r1|r2) get a
# divider; no lines inside a group, so Nominal/Misaligned/Delta visually
# stay together with their r0/r1/r2 header
_GROUP_SEPARATORS = [_COL_EDGES[1], _COL_EDGES[4], _COL_EDGES[7]]


def _param(fit, i):
    return fit.GetParameter(i), fit.GetParError(i)


def build_rows(graphs_n, graphs_m):
    gm_by_eta = {g["eta_index"]: g for g in graphs_m}
    rows = []
    for g_n in graphs_n:
        g_m = gm_by_eta.get(g_n["eta_index"])
        if g_m is None:
            continue
        f_n, f_m = g_n["fit"], g_m["fit"]
        row = {"eta": g_n["eta"]}
        for i, key in enumerate(("r0", "r1", "r2")):
            v_n, e_n = _param(f_n, i)
            v_m, e_m = _param(f_m, i)
            diff = v_m - v_n
            sigma = math.sqrt(e_n ** 2 + e_m ** 2)
            n_sigma = abs(diff) / sigma if sigma > 0 else float("inf")
            row[key] = {"n": (v_n, e_n), "m": (v_m, e_m),
                       "diff": diff, "sigma": sigma, "n_sigma": n_sigma}
        rows.append(row)
    return rows


def _fmt(val, err, scale=1.0, prec=3):
    return f"{val * scale:.{prec}f} #pm {err * scale:.{prec}f}"


def build_closure_table_pdf(rows, filename="table_closure_test.pdf"):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    output_path = os.path.join(IMAGES_DIR, filename)

    c = ROOT.TCanvas("c_table_closure", "Closure test table", 1500, 560)
    for setter in (c.SetLeftMargin, c.SetRightMargin,
                   c.SetTopMargin, c.SetBottomMargin):
        setter(0.0)
    c.Range(0, 0, 1, 1)

    x0, x1 = _COL_EDGES[0], _COL_EDGES[-1]
    keep = []

    title = ROOT.TLatex()
    title.SetTextFont(62)
    title.SetTextSize(0.044)
    title.SetTextAlign(22)
    title.DrawLatex(0.5, 0.94,
                    "Closure test: r_{0}, r_{1}, r_{2} nominal vs misaligned")
    keep.append(title)

    subtitle = ROOT.TLatex()
    subtitle.SetTextFont(42)
    subtitle.SetTextSize(0.022)
    subtitle.SetTextColor(ROOT.kGray + 2)
    subtitle.SetTextAlign(22)
    subtitle.DrawLatex(0.5, 0.885,
                       "r_{0}, r_{1} expected to match within uncertainties; "
                       "r_{2} is expected to change (misalignment effect)")
    keep.append(subtitle)

    n_rows = len(rows)
    top = 0.80
    bottom = 0.09
    header_h1 = 0.075
    header_h2 = 0.065
    row_h = (top - header_h1 - header_h2 - bottom) / n_rows

    # --- header row 1: group labels ---
    y_top = top
    header_box1 = ROOT.TBox(x0, y_top - header_h1, x1, y_top)
    header_box1.SetFillColor(_header_color)
    header_box1.Draw()
    keep.append(header_box1)

    hlat1 = ROOT.TLatex()
    hlat1.SetTextFont(62)
    hlat1.SetTextSize(0.026)
    hlat1.SetTextColor(ROOT.kWhite)
    hlat1.SetTextAlign(22)
    y_mid1 = y_top - header_h1 / 2.0
    hlat1.DrawLatex((_COL_EDGES[0] + _COL_EDGES[1]) / 2.0, y_mid1, "Region")
    for label, i_lo, i_hi in _GROUPS:
        xc = (_COL_EDGES[i_lo] + _COL_EDGES[i_hi]) / 2.0
        hlat1.DrawLatex(xc, y_mid1, label)
    keep.append(hlat1)

    # --- header row 2: sub-column labels ---
    y_top2 = y_top - header_h1
    header_box2 = ROOT.TBox(x0, y_top2 - header_h2, x1, y_top2)
    header_box2.SetFillColor(_header_color)
    header_box2.Draw()
    keep.append(header_box2)

    hlat2 = ROOT.TLatex()
    hlat2.SetTextFont(42)
    hlat2.SetTextSize(0.022)
    hlat2.SetTextColor(ROOT.kWhite)
    hlat2.SetTextAlign(22)
    y_mid2 = y_top2 - header_h2 / 2.0
    for i, label in enumerate(_SUBCOLS):
        xc = (_COL_EDGES[i + 1] + _COL_EDGES[i + 2]) / 2.0
        hlat2.DrawLatex(xc, y_mid2, label)
    keep.append(hlat2)

    y = y_top2 - header_h2
    body_lat = ROOT.TLatex()
    body_lat.SetTextFont(42)
    body_lat.SetTextSize(0.021)
    body_lat.SetTextAlign(22)

    warn_lat = ROOT.TLatex()
    warn_lat.SetTextFont(62)
    warn_lat.SetTextSize(0.021)
    warn_lat.SetTextColor(_bad_color)
    warn_lat.SetTextAlign(22)

    region_lat = ROOT.TLatex()
    region_lat.SetTextFont(42)
    region_lat.SetTextSize(0.021)
    region_lat.SetTextAlign(12)

    scales = {"r0": (1.0, 3), "r1": (1.0, 4), "r2": (1e3, 3)}

    for i, row in enumerate(rows):
        if i % 2 == 1:
            zebra = ROOT.TBox(x0, y - row_h, x1, y)
            zebra.SetFillColor(_zebra_color)
            zebra.SetLineWidth(0)
            zebra.Draw()
            keep.append(zebra)

        y_mid = y - row_h / 2.0
        region_lat.DrawLatex(_COL_EDGES[0] + 0.008, y_mid,
                             row["eta"]["label"])

        col = 1
        for key in ("r0", "r1", "r2"):
            scale, prec = scales[key]
            d = row[key]
            v_n, e_n = d["n"]
            v_m, e_m = d["m"]

            xc_n = (_COL_EDGES[col] + _COL_EDGES[col + 1]) / 2.0
            body_lat.DrawLatex(xc_n, y_mid, _fmt(v_n, e_n, scale, prec))

            xc_m = (_COL_EDGES[col + 1] + _COL_EDGES[col + 2]) / 2.0
            body_lat.DrawLatex(xc_m, y_mid, _fmt(v_m, e_m, scale, prec))

            xc_d = (_COL_EDGES[col + 2] + _COL_EDGES[col + 3]) / 2.0
            diff_txt = f"{d['diff'] * scale:+.{prec}f} ({d['n_sigma']:.1f}#sigma)"
            warn = key in ("r0", "r1") and d["n_sigma"] > _N_SIGMA_WARN
            (warn_lat if warn else body_lat).DrawLatex(xc_d, y_mid, diff_txt)

            col += 3

        y -= row_h

    table_bottom = y
    for xe in _GROUP_SEPARATORS:
        vline = ROOT.TLine(xe, table_bottom, xe, top)
        vline.SetLineColor(_header_color)
        vline.SetLineWidth(2)
        vline.Draw()
        keep.append(vline)
    border = ROOT.TBox(x0, table_bottom, x1, top)
    border.SetFillStyle(0)
    border.SetLineColor(_header_color)
    border.SetLineWidth(2)
    border.Draw()
    keep.append(border)

    footer = ROOT.TLatex()
    footer.SetTextFont(42)
    footer.SetTextSize(0.017)
    footer.SetTextColor(_bad_color)
    footer.SetTextAlign(22)
    footer.DrawLatex(0.5, table_bottom - 0.045,
                     f"In red: |#Delta| > {_N_SIGMA_WARN:.0f}#sigma_{{comb}} "
                     "on r_{0} or r_{1} -- closure test failed for that region")
    keep.append(footer)

    c.SaveAs(output_path)
    print(f"[INFO] Closure test table saved to {output_path}")
    return c, keep


def main():
    print(f"[INFO] Nominale:   {NOMINAL_ROOT}")
    print(f"[INFO] Misaligned: {MISALIGNED_ROOT}")

    histos_n, sums_n, counts_n = load(NOMINAL_ROOT)
    histos_m, sums_m, counts_m = load(MISALIGNED_ROOT)

    graphs_n = build_graphs_and_fits(histos_n, sums_n, counts_n,
                                     method="q68", fit_pt_max=PT_FIT_MAX,
                                     verbose=False)
    graphs_m = build_graphs_and_fits(histos_m, sums_m, counts_m,
                                     method="q68", fit_pt_max=PT_FIT_MAX,
                                     verbose=False)

    rows = build_rows(graphs_n, graphs_m)

    print("\n=== Closure test: r0/r1/r2 nominal vs misaligned ===")
    for row in rows:
        print(f"\n{row['eta']['label']}")
        for key in ("r0", "r1", "r2"):
            d = row[key]
            flag = " <-- NOT compatible" if (key in ("r0", "r1")
                    and d["n_sigma"] > _N_SIGMA_WARN) else ""
            print(f"  {key}: nominal={d['n'][0]:.5f}+-{d['n'][1]:.5f}  "
                  f"misaligned={d['m'][0]:.5f}+-{d['m'][1]:.5f}  "
                  f"diff={d['diff']:+.5f} ({d['n_sigma']:.2f} sigma){flag}")

    build_closure_table_pdf(rows)


if __name__ == "__main__":
    main()
