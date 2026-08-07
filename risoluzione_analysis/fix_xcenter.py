import re
import sys
import shutil

import ROOT
from config import PT_BINS, TREE_NAME

N_DEFAULT = 500_000


def find_bin(pt):
    for b in PT_BINS:
        if b["min"] <= pt < b["max"]:
            return b["name"]
    return None


def compute_means(path, n_max):
    chain = ROOT.TChain(TREE_NAME)
    chain.Add(path)
    print(f"[INFO] File: {path}")
    print(f"[INFO] Processo al massimo {n_max} eventi\n")

    chain.SetBranchStatus("*", 0)
    for br in ("muon_pt", "truthmuon_pt", "muon_truthmuon_index"):
        chain.SetBranchStatus(br, 1)

    somma = {b["name"]: 0.0 for b in PT_BINS}
    conta = {b["name"]: 0 for b in PT_BINS}

    for i, entry in enumerate(chain):
        if i >= n_max:
            break
        if i % 100000 == 0 and i:
            print(f"[INFO] {i} eventi", flush=True)

        muon_pt = entry.muon_pt
        truthmuon_pt = entry.truthmuon_pt
        truth_index = entry.muon_truthmuon_index

        for j in range(len(muon_pt)):
            idx = truth_index[j]
            if idx < 0 or idx >= len(truthmuon_pt):
                continue

            pt_reco = muon_pt[j] / 1000.0
            pt_truth = truthmuon_pt[idx] / 1000.0
            if pt_reco <= 0 or pt_truth <= 0:
                continue

            nome = find_bin(pt_truth)
            if nome is not None:
                somma[nome] += pt_truth
                conta[nome] += 1

    medie = {}
    for b in PT_BINS:
        n = conta[b["name"]]
        medie[b["name"]] = somma[b["name"]] / n if n > 0 else b["x_center"]
    return medie, conta


def update_config(medie, path="config.py"):
    shutil.copy(path, path + ".bak")
    print(f"\n[INFO] Backup salvato in {path}.bak")

    with open(path) as f:
        righe = f.readlines()

    nuove = []
    for riga in righe:
        for b in PT_BINS:
            if f'"name": "{b["name"]}"' in riga:
                nuovo = round(medie[b["name"]], 1)
                riga = re.sub(r'"x_center":\s*[0-9.]+',
                              f'"x_center": {nuovo}', riga)
                break
        nuove.append(riga)

    with open(path, "w") as f:
        f.writelines(nuove)
    print(f"[INFO] {path} aggiornato")


def main(path, n_max=N_DEFAULT):
    medie, conta = compute_means(path, n_max)

    print("\n" + "=" * 58)
    print(f"{'bin':>12} {'centro geom.':>14} {'<pT> reale':>12} {'muoni':>10}")
    print("=" * 58)
    for b in PT_BINS:
        print(f"{b['min']:>4}-{b['max']:<7} "
              f"{b['x_center']:>14} "
              f"{medie[b['name']]:>12.1f} "
              f"{conta[b['name']]:>10}")
    print("=" * 58)

    update_config(medie)
    print("\n[INFO] Ora rilancia:")
    print("       python3 merge.py /eos/user/m/masegret/risoluzione_out")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 fix_xcenter.py <file.root> [n_eventi]")
        sys.exit(1)
    main(sys.argv[1],
         int(sys.argv[2]) if len(sys.argv) > 2 else N_DEFAULT)
