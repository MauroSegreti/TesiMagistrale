import os
import sys
import glob
import subprocess

import ROOT
from config import WP_LIST, OUTPUT_ROOT_FILE
from plotting import build_efficiencies, save_all_plots
import style

style.apply_style()

EFF_VARS = ["pt", "eta", "phi"]


def main(outdir, merged="merged.root"):
    files = sorted(glob.glob(os.path.join(outdir, "job_*", "output_wp.root")))
    if not files:
        raise RuntimeError(f"Nessun output trovato in {outdir}")
    print(f"[INFO] {len(files)} file da unire")

    subprocess.run(["hadd", "-f", merged] + files, check=True)

    f = ROOT.TFile.Open(merged)

    def grab(name):
        h = f.Get(name)
        if not h:
            raise RuntimeError(f"Istogramma '{name}' non trovato in {merged}")
        h = h.Clone()
        h.SetDirectory(0)
        return h

    histos_res = {wp: grab(f"h_res_{wp}") for wp in WP_LIST}
    eff_histos = {
        var: {wp: grab(f"h_pass_{var}_{wp}") for wp in WP_LIST}
        for var in EFF_VARS
    }
    h_total = {var: grab(f"h_total_{var}") for var in EFF_VARS}
    f.Close()

    effs = build_efficiencies(eff_histos, h_total)

    out = ROOT.TFile(OUTPUT_ROOT_FILE, "RECREATE")
    for h in histos_res.values():
        h.Write()
    for var_histos in eff_histos.values():
        for h in var_histos.values():
            h.Write()
    for h in h_total.values():
        h.Write()
    for var_effs in effs.values():
        for eff in var_effs.values():
            eff.Write()
    out.Close()

    save_all_plots(histos_res, effs)

    print(f"\n[INFO] Muoni ricostruiti e matchati (totale) = {int(h_total['pt'].GetEntries())}")
    for wp in WP_LIST:
        n = int(eff_histos["pt"][wp].GetEntries())
        rms = histos_res[wp].GetRMS()
        print(f"  {wp:>6}: {n:>10} muoni passanti, RMS risoluzione = {rms:.4f}")
    print(f"[INFO] Salvato in {OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 merge.py <outdir>")
        sys.exit(1)
    main(sys.argv[1])
