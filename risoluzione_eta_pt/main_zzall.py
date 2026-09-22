"""
Come main.py, ma con la griglia di pT estesa fino a 1750 GeV (PT_BINS_EXT
qui sotto, 12 bin, al posto dei 6 di config.py che arrivano solo a 500
GeV) -- serve per unire Z e Z' aligned nella stessa statistica (i muoni
Z' vivono soprattutto sopra i 500 GeV, il picco di ciascuna risonanza e'
a M/2). ETA_BINS restano quelli di config.py.

Range troncato a 1750 GeV (tolti i due bin 1750-2500 e 2500-3000, che
c'erano nella primissima versione) su richiesta esplicita, per essere
coerente con main_zzdisall.py (Z+Z' disaligned, ferma anche lui a 1750
GeV). I job gia' girati con la vecchia griglia a 14 bin hanno comunque
salvato anche gli ultimi due istogrammi: restano nei file su EOS, solo
inutilizzati (merge_zzall.py adesso ne legge solo 12).

Un job per file (sia i 68 file di Z aligned sia i 5 file Z' aligned),
via gen_jobs_zzall.sh + condorSub_zzall.sub. Salva solo la griglia di
istogrammi (output_eta_ext.root): niente plot per-job, si fanno solo
dopo il merge (merge_zzall.py) con la statistica piena.

Uso: python3 main_zzall.py <input_path>
"""

import sys
import ROOT

from config import TREE_NAME, ETA_BINS, PROMPT_IFF_TYPE
from chain_builder import build_chain
import histograms
import event_loop

PT_BINS_EXT = [
    {"name": "20_30", "min": 20, "max": 30},
    {"name": "30_40", "min": 30, "max": 40},
    {"name": "40_50", "min": 40, "max": 50},
    {"name": "50_70", "min": 50, "max": 70},
    {"name": "70_100", "min": 70, "max": 100},
    {"name": "100_150", "min": 100, "max": 150},
    {"name": "150_200", "min": 150, "max": 200},
    {"name": "200_300", "min": 200, "max": 300},
    {"name": "300_500", "min": 300, "max": 500},
    {"name": "500_800", "min": 500, "max": 800},
    {"name": "800_1200", "min": 800, "max": 1200},
    {"name": "1200_1750", "min": 1200, "max": 1750},
]
histograms.PT_BINS = PT_BINS_EXT
event_loop.PT_BINS = PT_BINS_EXT

OUTPUT_ROOT_FILE = "output_eta_ext.root"


def save_histograms(histos, path=OUTPUT_ROOT_FILE):
    out = ROOT.TFile(path, "RECREATE")
    n = 0
    for p in PT_BINS_EXT:
        for h in histos[p["name"]]:
            h.Write()
            n += 1
    out.Close()
    print(f"[INFO] {n} istogrammi salvati in {path}")


def main(input_path):
    histos = histograms.build_histogram_grid()
    chain = build_chain(TREE_NAME, input_path)

    print("\n[INFO] Inizio loop eventi...\n")
    filled_muons, total_prompt = event_loop.process_events(chain, histos)

    print(f"\n[INFO] Muoni prompt processati = {total_prompt}")
    print(f"[INFO] Muoni riempiti negli istogrammi (pT 20-1750 GeV) = {filled_muons}")

    save_histograms(histos)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUso:\npython3 main_zzall.py <input_path>\n")
        sys.exit(1)

    main(sys.argv[1])
