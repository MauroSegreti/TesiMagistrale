"""
Fase 2: unisce gli output dei job, guarda i punti, fa i fit, costruisce le
sistematiche.

Uso:
    python3 analyze.py <cartella_output_job> [merged.root]

Il risultato nominale usa sigma_68 = (q84 - q16)/2 con errore
sigma/sqrt(2N). Vengono poi rifatti due fit alternativi:
  - stesso range, ma sigma dal fit gaussiano sul core
  - stessa sigma, ma range limitato a PT_MAX_VARIANT
La differenza rispetto al nominale e' la sistematica su metodo e range.
"""

import os
import sys
import glob
import subprocess

import ROOT

from config import (PT_BINS, ETA_BINS, PT_FIT_MAX, PT_MAX_VARIANT, PLOT_X_MAX)
from histograms import read_pt_means
from resolution import extract_width
from fitting import build_graphs_and_fits
from plotting import (draw_resolution_vs_pt, draw_estimator_comparison,
                      print_fit_parameters)
from report import build_table_pdf
from logtee import Tee
import style

style.apply_style()

LOG_FILE = "images/log_analisi.txt"


def load(merged):
    f = ROOT.TFile.Open(merged)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {merged}")

    def grab(name):
        h = f.Get(name)
        if not h:
            raise RuntimeError(f"'{name}' non trovato in {merged}")
        h = h.Clone()
        h.SetDirectory(0)
        return h

    histos = {e_i: [grab(f"h_res_eta_{e_i}_{p['name']}") for p in PT_BINS]
              for e_i in range(len(ETA_BINS))}
    h_sum, h_count = grab("h_pt_sum"), grab("h_pt_count")
    f.Close()

    pt_sums, pt_counts = read_pt_means(h_sum, h_count)
    return histos, pt_sums, pt_counts


def print_entries(histos):
    print("=== Entries per bin pT x eta ===")
    header = f"{'bin pT':>12}"
    for e in ETA_BINS:
        header += f"{'%.2f-%.2f' % (e['min'], e['max']):>13}"
    print(header)
    for p_i, p in enumerate(PT_BINS):
        row = f"{p['name']:>12}"
        for e_i in range(len(ETA_BINS)):
            row += f"{int(histos[e_i][p_i].GetEntries()):>13}"
        print(row)
    print()


def print_gaussianity(histos):
    """Quanto sono gaussiane le distribuzioni: la domanda di Luca."""
    print("=== Gaussianita': q68/gaus e asimmetria ===")
    print("    (q68/gaus ~ 1 e |asym| < 0.10 -> gaussiana)")
    header = f"{'bin pT':>12}"
    for e in ETA_BINS:
        header += f"{'%.2f-%.2f' % (e['min'], e['max']):>15}"
    print(header)
    for p_i, p in enumerate(PT_BINS):
        row = f"{p['name']:>12}"
        for e_i in range(len(ETA_BINS)):
            info = extract_width(histos[e_i][p_i], method="q68")
            if not info["ok"] or not info["sigma_gaus"]:
                row += f"{'--':>15}"
                continue
            ratio = info["sigma_q68"] / info["sigma_gaus"]
            row += f"{ratio:>8.2f}{info['asym']:>+7.2f}"
        print(row)
    print()


def print_local_slope(graphs):
    """
    Pendenza locale in log-log fra punti consecutivi:
        slope = d log(sigma) / d log(pT)
    Il modello prevede slope -> 1 ad alto pT (termine r2*pT dominante) e
    slope -> 0 nel plateau di multiple scattering. Se ad alto pT la
    pendenza resta ben sotto 1, la sigma NON cresce linearmente e la
    formula a tre termini non puo' descrivere i dati.
    """
    import math
    print("\n=== Pendenza locale d log(sigma) / d log(pT) ===")
    print("    (attesa ~0 nel plateau, ~1 dove domina il termine r2)")
    for g in graphs:
        pts = g["points"]
        if len(pts) < 2:
            continue
        print(f"\n  {g['eta']['label']}")
        print(f"    {'pT [GeV]':>22}{'sigma68':>11}{'slope':>9}")
        for a, b in zip(pts[:-1], pts[1:]):
            if a["sigma"] <= 0 or b["sigma"] <= 0 or a["pt"] <= 0:
                continue
            slope = math.log(b["sigma"] / a["sigma"]) / math.log(b["pt"] / a["pt"])
            print(f"    {a['pt']:>9.0f} -> {b['pt']:<9.0f}"
                  f"{b['sigma']:>11.4f}{slope:>9.2f}")
    print()


def r2_of(graphs, e_i):
    for g in graphs:
        if g["eta_index"] == e_i:
            return g["fit"].GetParameter(2) * 1e3, g["fit"].GetParError(2) * 1e3
    return None, None


def systematics_table(nominal, var_gaus, var_range):
    print("\n" + "=" * 94)
    print("r2 [10^-3 GeV^-1]: nominale (q68, range completo) e sistematiche")
    print("=" * 94)
    print(f"{'|eta| bin':>26}{'nominale':>12}{'stat':>9}"
          f"{'gaus':>10}{'d_metodo':>11}{'range 2TeV':>13}{'d_range':>11}")
    for e_i, e in enumerate(ETA_BINS):
        nom, stat = r2_of(nominal, e_i)
        if nom is None:
            continue
        gau, _ = r2_of(var_gaus, e_i)
        ran, _ = r2_of(var_range, e_i)
        row = f"{e['label']:>26}{nom:>12.4f}{stat:>9.4f}"
        row += f"{gau:>10.4f}{abs(gau-nom):>11.4f}" if gau else f"{'--':>10}{'--':>11}"
        row += f"{ran:>13.4f}{abs(ran-nom):>11.4f}" if ran else f"{'--':>13}{'--':>11}"
        print(row)
    print("=" * 94)

    print("\nRisultato con sistematiche sommate in quadratura:")
    for e_i, e in enumerate(ETA_BINS):
        nom, stat = r2_of(nominal, e_i)
        if nom is None:
            continue
        gau, _ = r2_of(var_gaus, e_i)
        ran, _ = r2_of(var_range, e_i)
        d1 = abs(gau - nom) if gau else 0.0
        d2 = abs(ran - nom) if ran else 0.0
        syst = (d1 ** 2 + d2 ** 2) ** 0.5
        print(f"  {e['label']:>26}:  r2 = {nom:.4f} +- {stat:.4f} (stat) "
              f"+- {syst:.4f} (syst)   [{100*syst/nom:.0f}% syst]")
    print()


def main(outdir, merged="merged_res.root"):
    files = sorted(glob.glob(os.path.join(outdir, "job_*", "output_res.root")))
    if not files:
        raise RuntimeError(f"Nessun output trovato in {outdir}")
    print(f"[INFO] {len(files)} file da unire")
    subprocess.run(["hadd", "-f", merged] + files, check=True)

    histos, pt_sums, pt_counts = load(merged)
    print_entries(histos)
    print_gaussianity(histos)

    print("\n" + "#" * 70)
    print(f"# NOMINALE: sigma_68, fit fino a {PT_FIT_MAX:.0f} GeV "
          f"(punti oltre restano nel grafico), r0 libero")
    print("#" * 70)
    nominal = build_graphs_and_fits(histos, pt_sums, pt_counts, method="q68",
                                    fit_pt_max=PT_FIT_MAX)
    if not nominal:
        print("[ERROR] nessun bin di eta valido")
        return 1
    print_local_slope(nominal)
    print_fit_parameters(nominal)
    draw_resolution_vs_pt(nominal, "plot_res_q68", x_max=PLOT_X_MAX,
                          subtitle="#sigma_{68} = (q_{84} - q_{16})/2")
    build_table_pdf(nominal, "table_res_q68.pdf")

    print("\n" + "#" * 70)
    print("# VARIANTE 1: sigma dal fit gaussiano (sistematica sul metodo)")
    print("#" * 70)
    var_gaus = build_graphs_and_fits(histos, pt_sums, pt_counts,
                                     method="gaus", fit_pt_max=PT_FIT_MAX,
                                     verbose=False)
    print_fit_parameters(var_gaus)
    draw_resolution_vs_pt(var_gaus, "plot_res_gaus", x_max=PLOT_X_MAX,
                          subtitle="Gaussian fit in #pm#sigma",
                          y_symbol="#sigma_{gauss}")

    print("\n" + "#" * 70)
    print(f"# VARIANTE 2: sigma_68, range fino a {PT_MAX_VARIANT:.0f} GeV")
    print("#" * 70)
    var_range = build_graphs_and_fits(histos, pt_sums, pt_counts,
                                      method="q68", pt_max=PT_MAX_VARIANT,
                                      verbose=False)
    print_fit_parameters(var_range)

    draw_estimator_comparison(nominal, var_gaus)
    systematics_table(nominal, var_gaus, var_range)

    print(f"[INFO] File unito: {merged}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso: python3 analyze.py <cartella_output_job> [merged.root]\n")
        sys.exit(1)
    with Tee(LOG_FILE):
        code = main(*sys.argv[1:3])
    sys.exit(code)
