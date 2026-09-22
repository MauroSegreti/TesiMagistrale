"""
Come merge_zzall.py, ma per Z disallineato + Z' disallineato (26 + 5 = 31
job, griglia pT estesa fino a 1750 GeV -- 12 bin, tolti gli ultimi due
usati per l'aligned in ZZallRMS). Genera gli stessi plot/tabella in
ZZdisallRMS/.

Uso:
    python3 merge_zzdisall.py /eos/user/m/masegret/risoluzione_zzdisall_out
"""

import os
import sys
import glob
import subprocess

import ROOT

from config import ETA_BINS
from main_zzdisall import PT_BINS_EXT
import histograms
import plotting
import report
import plot_rms_vs_pt_per_eta as pt_eta
import style

style.apply_style()

for mod in (histograms, plotting, pt_eta):
    mod.PT_BINS = PT_BINS_EXT

IMAGES_DIR = "ZZdisallRMS"
plotting.IMAGES_DIR = IMAGES_DIR
report.IMAGES_DIR = IMAGES_DIR
pt_eta.IMAGES_DIR = IMAGES_DIR

MERGED = "merged_ZZdisallRMS.root"


def load_grid(merged):
    f = ROOT.TFile.Open(merged)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {merged}")

    histos = {}
    for p in PT_BINS_EXT:
        histos[p["name"]] = []
        for e in ETA_BINS:
            name = f"h_res_{p['name']}_eta_{e['min']}_{e['max']}"
            h = f.Get(name)
            if not h:
                raise RuntimeError(f"Istogramma '{name}' non trovato in {merged}")
            h = h.Clone()
            h.SetDirectory(0)
            histos[p["name"]].append(h)
    f.Close()
    return histos


def main(outdir, merged=MERGED):
    files = sorted(glob.glob(os.path.join(outdir, "job_*", "output_eta_ext.root")))
    if not files:
        raise RuntimeError(f"Nessun output trovato in {outdir}")
    print(f"[INFO] {len(files)} file da unire")

    n_expected = len(glob.glob(os.path.join(outdir, "job_*")))
    if len(files) < n_expected:
        print(f"[WARN] {n_expected - len(files)} job senza output "
              f"(su {n_expected} attesi) -- si procede con quelli disponibili")

    histograms.check_binning(files, pt_bins=PT_BINS_EXT)
    subprocess.run(["hadd", "-f", merged] + files, check=True)

    histos = load_grid(merged)

    graphs, results = plotting.build_rms_graphs(histos)
    plotting.draw_rms_vs_eta(graphs, ylabel="RMS")
    plotting.draw_eta_overlay(histos)
    report.build_table_pdf(results)

    f = ROOT.TFile.Open(merged)
    for eta in ETA_BINS:
        points = pt_eta.load_points(f, eta)
        pt_eta.draw(points, eta, logx=True, ylabel="RMS")
    f.Close()

    totale = sum(r["entries"] for r in results)
    print(f"\n[INFO] Muoni totali negli istogrammi = {totale}")

    scarsi = [r for r in results if r["entries"] < 100]
    if scarsi:
        print(f"\n[WARN] {len(scarsi)} bin con meno di 100 muoni:")
        for r in scarsi:
            print(f"  pT {r['pt_min']}-{r['pt_max']} GeV, "
                  f"|eta| [{r['eta_min']}, {r['eta_max']}): {r['entries']} muoni")

    print(f"\n[INFO] File unito: {merged}")
    print(f"[INFO] Plot e tabella in {IMAGES_DIR}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 merge_zzdisall.py <outdir>")
        sys.exit(1)
    main(sys.argv[1])
