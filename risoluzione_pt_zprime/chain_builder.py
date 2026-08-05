"""
Costruzione della TChain di ROOT a partire da uno o piu' input path.
Isolato in un suo file perché è pura logica di I/O, separata
dall'analisi vera e propria.

build_chain accetta uno o PIU' path (build_chain(tree_name, path1, path2, ...)),
tutti aggiunti alla stessa TChain -- utile per combinare sample che
vivono in cartelle separate (es. la Z standard in una cartella e i
vari Zp in un'altra), senza doverli per forza mettere tutti insieme
nella stessa cartella.

Ogni singolo path viene classificato guardando il filesystem, non la stringa:
1. file .root                    -> viene aggiunto direttamente
2. file .root.txt (lista Rucio)  -> vengono letti gli URL root://
   contenuti dentro e aggiunti alla chain
3. cartella                      -> viene cercato ricorsivamente sia
   *ANALYSIS.root* (file locali gia' disponibili, anche se il job grid li
   ha splittati in "...ANALYSIS.root.1", "...ANALYSIS.root.2" ecc.) sia
   *.root.txt (liste Rucio con URL remoti da leggere via XRootD)
"""

import os
import glob
import ROOT


def _read_urls_from_txt(txt_path):
    """Legge un file .root.txt (lista Rucio) e ritorna gli URL root:// al suo interno,
    una riga per URL, ignorando righe vuote."""
    with open(txt_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def _add_path_to_chain(chain, path):
    """Aggiunge un singolo path (file .root, lista .txt o cartella) alla chain.
    Il tipo di path viene deciso guardando il FILESYSTEM (os.path.isfile /
    os.path.isdir), non il suffisso della stringa: su EOS/grid capita che una
    CARTELLA di un dataset si chiami "...ANALYSIS.root" (o finisca proprio con
    "ANALYSIS.root/") -- trattarla come singolo file solo perche' la stringa
    finisce in ".root" sarebbe sbagliato (chain vuota, senza nessun errore
    esplicito).
    Ritorna la lista degli "identificatori" (nomi file/URL) aggiunti -- serve
    solo per poter controllare dopo, per stringa, quali DSID sono stati inclusi
    (es. accorgersi se manca la Z standard, vedi build_chain)."""

    # --- Caso 1: e' un file (.root singolo, o lista Rucio .txt) ---
    if os.path.isfile(path):
        if path.endswith(".txt"):
            urls = _read_urls_from_txt(path)
            for u in urls:
                chain.Add(u)
            print(f"[INFO] Aggiunti {len(urls)} file da lista Rucio: {path}")
            return [path] + urls

        chain.Add(path)
        print(f"[INFO] Aggiunto file singolo: {path}")
        return [path]

    # --- Caso 2: e' una cartella -> cerca ricorsivamente sia file .root
    #     locali sia liste Rucio .root.txt. Il pattern "*ANALYSIS.root*"
    #     (invece di richiedere che il nome finisca esattamente in
    #     ".root") prende anche l'output di job grid splittati in piu'
    #     file tipo "..._ANALYSIS.root.1", "..._ANALYSIS.root.2" ---
    if os.path.isdir(path):
        root_files = glob.glob(os.path.join(path, "**", "*ANALYSIS.root*"), recursive=True)
        root_files = [f for f in root_files if os.path.isfile(f) and not f.endswith(".txt")]

        txt_files = glob.glob(os.path.join(path, "**", "*.root.txt"), recursive=True)
        txt_files = [f for f in txt_files if os.path.isfile(f)]

        for f in root_files:
            chain.Add(f)

        identifiers = list(root_files)
        n_urls = 0
        for t in txt_files:
            urls = _read_urls_from_txt(t)
            for u in urls:
                chain.Add(u)
            identifiers.append(t)
            identifiers.extend(urls)
            n_urls += len(urls)

        print(f"[INFO] Cartella '{path}': {len(root_files)} file .root locali, "
              f"{n_urls} file remoti da {len(txt_files)} liste Rucio (.root.txt)")

        if len(root_files) == 0 and len(txt_files) == 0:
            print(f"[WARNING] Nessun file trovato in '{path}' "
                  f"(ne' *ANALYSIS.root* ne' *.root.txt) -- controlla il path.")

        return identifiers

    print(f"[WARNING] Path non trovato (ne' file ne' cartella): {path}")
    return []


def build_chain(tree_name, *paths, warn_missing_dsid="601190"):
    """
    warn_missing_dsid: se dato (default: 601190, il DSID della Z standard --
    vedi config.py), controlla che almeno uno dei nomi file/URL aggiunti alla
    chain lo contenga, e stampa un warning se manca. E' un controllo "morbido"
    a livello di stringa (funziona perche' il DSID compare nel nome dei file
    e delle liste Rucio, per convenzione ATLAS) -- serve a scoprire subito se
    ci si e' dimenticati di includere la Z, invece di accorgersene solo dopo
    aver girato tutta l'analisi.
    """
    if not paths:
        raise ValueError("build_chain ha bisogno di almeno un path")

    chain = ROOT.TChain(tree_name)
    all_identifiers = []
    for path in paths:
        all_identifiers.extend(_add_path_to_chain(chain, path))

    print(f"[INFO] Entries totali (tutti i path combinati) = {chain.GetEntries()}")

    if warn_missing_dsid and not any(warn_missing_dsid in s for s in all_identifiers):
        print(f"\n[WARNING] Nessun file/URL con DSID {warn_missing_dsid} (Z standard) trovato "
              f"tra i path forniti: stai combinando solo campioni Z'? Se ti serve anche la Z, "
              f"aggiungi il path o la lista Rucio corrispondente come argomento in piu'.\n")

    return chain
