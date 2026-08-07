import os
import glob
import ROOT


def _read_urls_from_txt(txt_path):
    with open(txt_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def _add_path_to_chain(chain, path):
    if os.path.isfile(path):
        if path.endswith(".txt"):
            urls = _read_urls_from_txt(path)
            for u in urls:
                chain.Add(u)
            print(f"[INFO] Aggiunti {len(urls)} file da lista: {path}")
            return [path] + urls

        chain.Add(path)
        print(f"[INFO] Aggiunto file singolo: {path}")
        return [path]

    if os.path.isdir(path):
        root_files = glob.glob(os.path.join(path, "**", "*ANALYSIS.root*"),
                               recursive=True)
        root_files = [f for f in root_files
                      if os.path.isfile(f) and not f.endswith(".txt")]

        txt_files = glob.glob(os.path.join(path, "**", "*.root.txt"),
                              recursive=True)
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

        print(f"[INFO] Cartella '{path}': {len(root_files)} file locali, "
              f"{n_urls} file remoti da {len(txt_files)} liste")

        if not root_files and not txt_files:
            print(f"[WARNING] Nessun file trovato in '{path}'")

        return identifiers

    print(f"[WARNING] Path non trovato: {path}")
    return []


def build_chain(tree_name, *paths, warn_missing_dsid="601190"):
    if not paths:
        raise ValueError("build_chain ha bisogno di almeno un path")

    chain = ROOT.TChain(tree_name)
    all_identifiers = []
    for path in paths:
        all_identifiers.extend(_add_path_to_chain(chain, path))

    if warn_missing_dsid and not any(warn_missing_dsid in s
                                     for s in all_identifiers):
        print(f"[INFO] Nessun file con DSID {warn_missing_dsid} (Z standard) "
              f"in questo job: normale se il job legge solo file di Z'.")

    return chain