import os
import glob
import ROOT


def _add_from_txt(chain, path):
    n, bad = 0, []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fh = ROOT.TFile.Open(line)
            if not fh or fh.IsZombie():
                bad.append(line)
                continue
            fh.Close()
            chain.Add(line)
            n += 1
    print(f"[INFO] Lista '{path}': aggiunti {n} file, {len(bad)} non apribili")
    for b in bad[:5]:
        print(f"  [WARN] KO: {b}")
    return n


def _add_from_dir(chain, path):
    root_files = glob.glob(
        os.path.join(path, "**", "*.ANALYSIS.root"), recursive=True
    )
    root_files = sorted(f for f in root_files if os.path.isfile(f))
    for f in root_files:
        chain.Add(f)
    print(f"[INFO] Directory '{path}': aggiunti {len(root_files)} file")
    return len(root_files)


def build_chain(tree_name, path):
    chain = ROOT.TChain(tree_name)

    # NB: il controllo sulla directory deve venire PRIMA di quello su '.root',
    # perche' le directory create da rucio si chiamano '<dataset>.ANALYSIS.root'
    # e altrimenti verrebbero trattate come file singoli.
    if os.path.isdir(path):
        _add_from_dir(chain, path)
    elif path.endswith(".txt"):
        _add_from_txt(chain, path)
    elif path.endswith(".root"):
        chain.Add(path)
        print(f"[INFO] Aggiunto file singolo: {path}")
    else:
        raise ValueError(f"Input non riconosciuto: {path}")

    n_entries = chain.GetEntries()
    print(f"[INFO] Entries totali = {n_entries}")
    if n_entries == 0:
        raise RuntimeError(
            f"Chain vuota: controlla il path e che il TTree si chiami '{tree_name}'"
        )

    return chain


def enable_branches(chain, branches):
    chain.SetBranchStatus("*", 0)
    for b in branches:
        chain.SetBranchStatus(b, 1)
    print(f"[INFO] Branch attivi: {', '.join(branches)}")
