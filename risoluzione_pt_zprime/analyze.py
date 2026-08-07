"""
Fase 2: unisce gli output dei job, fa i fit e produce plot e tabella.

Uso:
    python3 analyze.py <cartella_output_job> [merged.root]

Produce due versioni del risultato: una che usa tutti i punti fino a 3 TeV e
una limitata a 2 TeV, dove la statistica per bin e' piu' solida. Confrontare
r2 fra le due dice quanto i punti ad alto pT stanno influenzando il fit.
"""

import os
import sys
import glob
import subprocess

import ROOT

from config import PT_BINS, ETA_BINS
from histograms import read_pt_means
from fitting import build_graphs_and_fits
from plotting import draw_resolution_vs_pt, print_fit_parameters
from report import build_table_pdf
import style

style.apply_style()

CONFIGS = [
    {"pt_max": None, "tag": "3TeV", "x_max": 3500},
    {"pt_max": 2000, "tag": "2TeV", "x_max": 2200},
]


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

    histos = {}
    for e_i in range(len(ETA_BINS)):
        histos[e_i] = [grab(f"h_res_eta_{e_i}_{p['name']}") for p in PT_BINS]

    h_sum = grab("h_pt_sum")
    h_count = grab("h_pt_count")
    f.Close()

    pt_sums, pt_counts = read_pt_means(h_sum, h_count)
    return histos, pt_sums, pt_counts


def print_entries_table(histos):
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


def print_abscissa_shift(pt_sums, pt_counts):
    print("=== Ascissa: centro geometrico vs pT medio effettivo ===")
    print(f"{'bin pT':>14} {'centro':>9} {'medio':>9} {'shift':>8}")
    for p_i, p in enumerate(PT_BINS):
        tot_n = sum(pt_counts[e_i][p_i] for e_i in range(len(ETA_BINS)))
        tot_s = sum(pt_sums[e_i][p_i] for e_i in range(len(ETA_BINS)))
        if tot_n == 0:
            continue
        mean_eff = tot_s / tot_n
        print(f"{p['name']:>14} {p['mean']:9.0f} {mean_eff:9.0f} "
              f"{100*(mean_eff/p['mean']-1):+7.1f}%")
    print()


def summarize(results):
    print("\n" + "=" * 70)
    print("CONFRONTO r2 FRA LE DUE VERSIONI  [10^-3 GeV^-1]")
    print("=" * 70)
    tags = [r["tag"] for r in results]
    print(f"{'|eta| bin':>26}" + "".join(f"{t:>12}" for t in tags) + f"{'diff':>10}")
    labels = [g["eta"]["label"] for g in results[0]["graphs"]]
    for label in labels:
        row = f"{label:>26}"
        vals = []
        for r in results:
            match = [g for g in r["graphs"] if g["eta"]["label"] == label]
            if match:
                v = match[0]["fit"].GetParameter(2) * 1e3
                vals.append(v)
                row += f"{v:>12.4f}"
            else:
                row += f"{'--':>12}"
        if len(vals) == 2 and vals[0] != 0:
            row += f"{100*(vals[1]/vals[0]-1):>9.1f}%"
        print(row)
    print("=" * 70 + "\n")


def main(outdir, merged="merged_res.root"):
    files = sorted(glob.glob(os.path.join(outdir, "job_*", "output_res.root")))
    if not files:
        raise RuntimeError(f"Nessun output trovato in {outdir}")
    print(f"[INFO] {len(files)} file da unire")

    subprocess.run(["hadd", "-f", merged] + files, check=True)

    histos, pt_sums, pt_counts = load(merged)
    print_entries_table(histos)
    print_abscissa_shift(pt_sums, pt_counts)

    results = []
    for cfg in CONFIGS:
        limite = "nessun limite" if cfg["pt_max"] is None else f"pT < {cfg['pt_max']} GeV"
        print("\n" + "#" * 70)
        print(f"# VERSIONE {cfg['tag']}  ({limite})")
        print("#" * 70)

        graphs = build_graphs_and_fits(histos, pt_sums, pt_counts,
                                       pt_max=cfg["pt_max"])
        if not graphs:
            print(f"[ERROR] Nessun bin di eta valido per la versione {cfg['tag']}")
            continue

        draw_resolution_vs_pt(graphs, f"plot_res_vs_pt_{cfg['tag']}",
                              x_max=cfg["x_max"])
        print_fit_parameters(graphs)
        build_table_pdf(graphs, f"table_res_vs_pt_{cfg['tag']}.pdf")

        results.append({"tag": cfg["tag"], "graphs": graphs})

    if len(results) == 2:
        summarize(results)

    print(f"[INFO] File unito: {merged}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 analyze.py <cartella_output_job> [merged.root]\n")
        sys.exit(1)
    sys.exit(main(*sys.argv[1:3]))
