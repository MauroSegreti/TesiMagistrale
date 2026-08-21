import sys
import ROOT

from config import TREE_NAME, OUTPUT_ROOT_FILE, ACTIVE_BRANCHES
from chain_builder import build_chain, enable_branches
from histograms import build_histogram_set
from event_loop import process_events
from plotting import build_efficiencies, save_all_plots
import style

style.apply_style()


def main(input_path):
    histos_res, eff_histos, h_total = build_histogram_set()

    chain = build_chain(TREE_NAME, input_path)
    enable_branches(chain, ACTIVE_BRANCHES)

    print("\n[INFO] Inizio loop eventi...\n")
    filled_muons = process_events(chain, histos_res, eff_histos, h_total)

    out_file = ROOT.TFile(OUTPUT_ROOT_FILE, "RECREATE")
    for h in histos_res.values():
        h.Write()
    for var_histos in eff_histos.values():
        for h in var_histos.values():
            h.Write()
    for h in h_total.values():
        h.Write()
    out_file.Close()

    effs = build_efficiencies(eff_histos, h_total)
    save_all_plots(histos_res, effs)

    print("\n[INFO] Muoni ricostruiti e matchati =", filled_muons)
    for wp in histos_res:
        print(f"[INFO] Muoni passanti {wp} = {int(eff_histos['pt'][wp].GetEntries())}")
    print("[INFO] File ROOT salvato:", OUTPUT_ROOT_FILE)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:")
        print("python3 main.py <input_path>\n")
        sys.exit(1)

    main(sys.argv[1])
