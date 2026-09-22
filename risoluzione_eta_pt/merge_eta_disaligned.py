"""
Come merge_eta.py, ma per il campione Z disallineato (MisAligned_MC): unisce
gli output dei 26 job condor (uno per file, vedi gen_jobs_eta_disaligned.sh)
e rigenera plot e tabella con la statistica completa. Output in images2/, per
non toccare i risultati del campione allineato in images/.

Uso:
    python3 merge_eta_disaligned.py /eos/user/m/masegret/risoluzione_eta_disaligned_out
"""

import os
import sys
import glob
import subprocess

import ROOT

from config import PT_BINS, ETA_BINS
import histograms
import plotting
import report
import plot_rms_vs_pt_per_eta as pt_eta
import style

style.apply_style()

plotting.IMAGES_DIR = "images2"
report.IMAGES_DIR = "images2"
pt_eta.IMAGES_DIR = "images2"

MERGED = "merged_eta_disaligned.root"


def load_grid(merged):
    """Ricostruisce il dict { nome_bin_pt: [h_eta_0, h_eta_1, ...] }."""
    f = ROOT.TFile.Open(merged)
    if not f or f.IsZombie():
        raise RuntimeError(f"Impossibile aprire {merged}")

    histos = {}
    for p in PT_BINS:
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
    files = sorted(glob.glob(os.path.join(outdir, "job_*", "output_eta.root")))
    if not files:
        raise RuntimeError(f"Nessun output trovato in {outdir}")
    print(f"[INFO] {len(files)} file da unire")

    n_expected = len(glob.glob(os.path.join(outdir, "job_*")))
    if len(files) < n_expected:
        print(f"[WARN] {n_expected - len(files)} job senza output "
              f"(su {n_expected} attesi) -- si procede con quelli disponibili")

    histograms.check_binning(files)
    subprocess.run(["hadd", "-f", merged] + files, check=True)

    histos = load_grid(merged)

    graphs, results = plotting.build_rms_graphs(histos)
    plotting.draw_rms_vs_eta(graphs)
    plotting.draw_eta_overlay(histos)
    report.build_table_pdf(results)

    f = ROOT.TFile.Open(merged)
    for eta in ETA_BINS:
        points = pt_eta.load_points(f, eta)
        pt_eta.draw(points, eta)
    f.Close()

    totale = sum(r["entries"] for r in results)
    print(f"\n[INFO] Muoni totali negli istogrammi = {totale}")

    scarsi = [r for r in results if r["entries"] < 100]
    if scarsi:
        print(f"\n[WARN] {len(scarsi)} bin con meno di 100 muoni:")
        for r in scarsi:
            print(f"  pT {r['pt_min']}-{r['pt_max']} GeV, "
                  f"|eta| [{r['eta_min']}, {r['eta_max']}): "
                  f"{r['entries']} muoni")

    print(f"\n[INFO] File unito: {merged}")
    print("[INFO] Plot: images2/plot_RMS_vs_eta.png")
    print("[INFO] Plot overlay eta: images2/plot_eta_overlay.png")
    print("[INFO] Plot RMS vs pT per bin di eta: images2/RMS_*.png")
    print("[INFO] Tabella: images2/table_RMS_vs_eta.pdf")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 merge_eta_disaligned.py <outdir>")
        sys.exit(1)
    main(sys.argv[1])
