"""
Fase 1: riempie la griglia eta x pT e la salva su file ROOT.

Uso:
    python3 fill.py <file_o_lista_1> [<file_o_lista_2> ...] [-o output.root]

E' quello che lancia ogni job condor, su un file (o una piccola lista) alla
volta. Il fit NON viene fatto qui: serve la statistica di tutti i sample
insieme, quindi si fa dopo con analyze.py sul merge.
"""

import sys
import ROOT

from config import TREE_NAME, OUTPUT_ROOT_FILE, PT_BINS, ETA_BINS
from chain_builder import build_chain
from histograms import (build_histogram_grid, build_pt_accumulators,
                        print_window_summary)
from event_loop import process_events


def save(histos, h_sum, h_count, path):
    out = ROOT.TFile(path, "RECREATE")
    n = 0
    for e_i in range(len(ETA_BINS)):
        for h in histos[e_i]:
            h.Write()
            n += 1
    h_sum.Write()
    h_count.Write()
    out.Close()
    print(f"[INFO] {n} istogrammi + accumulatori salvati in {path}")


def main(paths, out_path=OUTPUT_ROOT_FILE):
    print_window_summary()

    chain = build_chain(TREE_NAME, *paths)
    n = chain.GetEntries()
    print(f"[INFO] Entries totali = {n}")
    if n == 0:
        print("[ERROR] Chain vuota. Verifica i path passati.")
        return 1

    histos = build_histogram_grid()
    h_sum, h_count = build_pt_accumulators()

    print("\n[INFO] Inizio loop eventi...\n")
    filled = process_events(chain, histos, h_sum, h_count)

    if filled == 0:
        print("[ERROR] Nessun muone riempito nei bin.")
        return 1

    save(histos, h_sum, h_count, out_path)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    out = OUTPUT_ROOT_FILE
    if "-o" in args:
        k = args.index("-o")
        out = args[k + 1]
        args = args[:k] + args[k + 2:]

    if not args:
        print("\nUso:")
        print("python3 fill.py <file_o_lista_1> [...] [-o output.root]\n")
        sys.exit(1)

    sys.exit(main(args, out))
