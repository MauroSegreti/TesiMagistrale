import os
import sys
import glob
import subprocess

import ROOT
from config import PT_BINS, OUTPUT_ROOT_FILE
from plotting import make_rms_graph, save_all_plots, draw_prompt_vs_inclusive
import style

style.apply_style()


def main(outdir, merged="merged.root"):
    files = sorted(glob.glob(os.path.join(outdir, "job_*", "output_risoluzione.root")))
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

    h_all = grab("h_res_all")
    h_all_prompt = grab("h_res_all_prompt")
    histos_pt = {b["name"]: grab(f"h_res_{b['name']}") for b in PT_BINS}
    histos_pt_prompt = {b["name"]: grab(f"h_res_{b['name']}_prompt") for b in PT_BINS}
    f.Close()

    graph = make_rms_graph(histos_pt, "g_rms_vs_pt",
                           "p_{T} Resolution; p_{T}^{truth} [GeV]; RMS")
    graph_prompt = make_rms_graph(histos_pt_prompt, "g_rms_vs_pt_prompt",
                                  "p_{T} Resolution (prompt); p_{T}^{truth} [GeV]; RMS")

    out = ROOT.TFile(OUTPUT_ROOT_FILE, "RECREATE")
    h_all.Write()
    for h in histos_pt.values():
        h.Write()
    h_all_prompt.Write()
    for h in histos_pt_prompt.values():
        h.Write()
    graph.Write()
    graph_prompt.Write()
    out.Close()

    save_all_plots(h_all, histos_pt, graph)
    save_all_plots(h_all_prompt, histos_pt_prompt, graph_prompt, suffix="_prompt")
    draw_prompt_vs_inclusive(h_all, h_all_prompt)

    print(f"\n[INFO] Muoni totali (inclusivo) = {int(h_all.GetEntries())}")
    print(f"[INFO] Muoni totali (prompt)    = {int(h_all_prompt.GetEntries())}")
    for b in PT_BINS:
        print(f"  {b['min']:>4}-{b['max']:<4} GeV: "
              f"{int(histos_pt[b['name']].GetEntries()):>10} muoni, "
              f"RMS = {histos_pt[b['name']].GetRMS():.4f}")
    print(f"[INFO] Salvato in {OUTPUT_ROOT_FILE}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 merge.py <outdir>")
        sys.exit(1)
    main(sys.argv[1])
