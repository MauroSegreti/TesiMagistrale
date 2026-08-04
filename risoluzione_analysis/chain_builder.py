"""
Costruzione della TChain di ROOT a partire da un input path.
Isolato in un suo file perché è pura logica di I/O, separata
dall'analisi vera e propria.
"""

import os
import glob
import ROOT


def build_chain(tree_name, path):
    """
    Se 'path' è un file .root, aggiunge solo quello.
    Altrimenti cerca ricorsivamente tutti i file *.ANALYSIS.root
    dentro la cartella indicata.
    """
    chain = ROOT.TChain(tree_name)

    if path.endswith(".root"):
        chain.Add(path)
        print(f"[INFO] Aggiunto file singolo: {path}")
        print(f"[INFO] Entries totali = {chain.GetEntries()}")
        return chain

    root_files = glob.glob(
        os.path.join(path, "**", "*.ANALYSIS.root"),
        recursive=True
    )
    root_files = [f for f in root_files if os.path.isfile(f)]

    for f in root_files:
        chain.Add(f)

    print(f"[INFO] Aggiunti {len(root_files)} file")
    print(f"[INFO] Entries totali = {chain.GetEntries()}")

    return chain
