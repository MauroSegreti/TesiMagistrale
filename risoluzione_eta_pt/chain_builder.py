"""
Costruzione della TChain di ROOT a partire da un input path.
Isolato in un suo file perché è pura logica di I/O, separata
dall'analisi vera e propria.

Gestisce tre casi:
1. path a un singolo file .root                -> lo aggiunge direttamente
2. path a un singolo file .root.txt (Rucio)     -> legge gli URL root://
   contenuti dentro e li aggiunge alla chain
3. path a una cartella                          -> cerca ricorsivamente sia
   *.ANALYSIS.root (file locali già disponibili) sia *.root.txt (liste Rucio
   con URL remoti da leggere via XRootD)
"""

import os
import glob
import ROOT


def _read_urls_from_txt(txt_path):
    """Legge un file .root.txt (lista Rucio) e ritorna gli URL root:// al suo interno,
    una riga per URL, ignorando righe vuote."""
    with open(txt_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def build_chain(tree_name, path):
    chain = ROOT.TChain(tree_name)

    # --- Caso 1: singolo file .root locale/remoto ---
    if path.endswith(".root"):
        chain.Add(path)
        print(f"[INFO] Aggiunto file singolo: {path}")
        print(f"[INFO] Entries totali = {chain.GetEntries()}")
        return chain

    # --- Caso 2: singola lista Rucio (.root.txt) ---
    if path.endswith(".txt"):
        urls = _read_urls_from_txt(path)
        for u in urls:
            chain.Add(u)
        print(f"[INFO] Aggiunti {len(urls)} file da lista Rucio: {path}")
        print(f"[INFO] Entries totali = {chain.GetEntries()}")
        return chain

    # --- Caso 3: cartella -> cerca sia file locali sia liste Rucio ---
    root_files = glob.glob(
        os.path.join(path, "**", "*.ANALYSIS.root"),
        recursive=True
    )
    root_files = [f for f in root_files if os.path.isfile(f)]

    txt_files = glob.glob(
        os.path.join(path, "**", "*.root.txt"),
        recursive=True
    )
    txt_files = [f for f in txt_files if os.path.isfile(f)]

    for f in root_files:
        chain.Add(f)

    n_urls = 0
    for t in txt_files:
        urls = _read_urls_from_txt(t)
        for u in urls:
            chain.Add(u)
        n_urls += len(urls)

    print(f"[INFO] Aggiunti {len(root_files)} file .root locali")
    print(f"[INFO] Aggiunti {n_urls} file remoti da {len(txt_files)} liste Rucio (.root.txt)")
    print(f"[INFO] Entries totali = {chain.GetEntries()}")

    return chain
