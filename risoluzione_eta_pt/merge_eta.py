"""
Unisce gli output dei job condor dell'analisi in eta e rigenera plot e
tabella con la statistica completa.

Gli istogrammi si sommano con hadd; i TGraphErrors no, vanno ricostruiti
dagli istogrammi sommati (e' quello che fa build_rms_graphs).

Uso:
    python3 merge_eta.py /eos/user/m/masegret/risoluzione_eta_out
"""

import os
import sys
import glob
import subprocess

import ROOT

from config import PT_BINS, ETA_BINS
from plotting import build_rms_graphs, draw_rms_vs_eta
from report import build_table_pdf
import style

style.apply_style()


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


def main(outdir, merged="merged_eta.root"):
    files = sorted(glob.glob(os.path.join(outdir, "job_*", "output_eta.root")))
    if not files:
        raise RuntimeError(f"Nessun output trovato in {outdir}")
    print(f"[INFO] {len(files)} file da unire")

    subprocess.run(["hadd", "-f", merged] + files, check=True)

    histos = load_grid(merged)

    graphs, results = build_rms_graphs(histos)
    draw_rms_vs_eta(graphs)
    build_table_pdf(results)

    totale = sum(r["entries"] for r in results)
    print(f"\n[INFO] Muoni totali negli istogrammi = {totale}")

    # segnala i bin con statistica troppo bassa perche' l'RMS sia affidabile
    scarsi = [r for r in results if r["entries"] < 100]
    if scarsi:
        print(f"\n[WARN] {len(scarsi)} bin con meno di 100 muoni:")
        for r in scarsi:
            print(f"  pT {r['pt_min']}-{r['pt_max']} GeV, "
                  f"|eta| [{r['eta_min']}, {r['eta_max']}): "
                  f"{r['entries']} muoni")

    print(f"\n[INFO] File unito: {merged}")
    print("[INFO] Plot: images/plot_RMS_vs_eta.png")
    print("[INFO] Tabella: images/table_RMS_vs_eta.pdf")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 merge_eta.py <outdir>")
        sys.exit(1)
    main(sys.argv[1])
