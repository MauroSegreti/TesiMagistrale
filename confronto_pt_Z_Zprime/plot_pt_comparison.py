"""
Confronto tra il p_T dei muoni ricostruiti nel campione Z->mumu (fondo/calibrazione,
DSID 601190) e nei campioni Z'->mumu a cinque punti di massa (500/1000/3000/5000/8000
GeV, DSID 801862-801866). 5000 e 8000 GeV erano stati esclusi/mai scaricati in
precedenza (v. README.md), poi scaricati con 'rucio download' (RSE MPPMU_PERF-MUONS,
protocollo davs) su richiesta esplicita.

Uso: python3 plot_pt_comparison.py
"""

import glob
import os

import ROOT

import style

style.apply_style()

ANADIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ANADIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

TREE_NAME = "AnalysisTree"

SAMPLES = [
    {
        # #mu^{+}#mu^{-} invece di #mu#mu: due "#mu" attaccati, a piccola
        # dimensione in legenda, si fondono visivamente in qualcosa che
        # sembra un simbolo di infinito. Con le cariche esplicite si separano
        # ed e' anche la notazione fisica standard per il decadimento.
        "label": "Z #rightarrow #mu^{+}#mu^{-}",
        "dir": "/eos/user/m/masegret/PerfectAlignment/"
               "user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu."
               "MCP_TESTNTUP.mc23e_ANALYSIS.root",
        "color": style.PALETTE[0],
        # campione da 68 file (~100M eventi): leggerlo tutto interattivamente
        # e' troppo lento (v. README di risoluzione_analysis, serve HTCondor).
        # Per un plot di forma normalizzato bastano poche decine di file.
        "max_files": 20,
    },
    {
        "label": "Z' 500 GeV",
        "dir": "/eos/user/m/masegret/dati_locali/"
               "user.mmarr.mc23_13p6TeV.801862.Py8EG_A14NNPDF23LO_Zp_mm_ZeroWidth500."
               "MCP_TESTNTUP.mc23e_ANALYSIS.root",
        "color": style.PALETTE[1],
        "max_files": None,
    },
    {
        "label": "Z' 1000 GeV",
        "dir": "/eos/user/m/masegret/dati_locali/"
               "user.mmarr.mc23_13p6TeV.801863.Py8EG_A14NNPDF23LO_Zp_mm_ZeroWidth1000."
               "MCP_TESTNTUP.mc23e_ANALYSIS.root",
        "color": style.PALETTE[2],
        "max_files": None,
    },
    {
        "label": "Z' 3000 GeV",
        "dir": "/eos/user/m/masegret/dati_locali/"
               "user.mmarr.mc23_13p6TeV.801864.Py8EG_A14NNPDF23LO_Zp_mm_ZeroWidth3000."
               "MCP_TESTNTUP.mc23e_ANALYSIS.root",
        "color": style.PALETTE[3],
        "max_files": None,
    },
    {
        "label": "Z' 5000 GeV",
        "dir": "/eos/user/m/masegret/dati_locali/"
               "user.mmarr.mc23_13p6TeV.801865.Py8EG_A14NNPDF23LO_Zp_mm_ZeroWidth5000."
               "MCP_TESTNTUP.mc23e_ANALYSIS.root",
        "color": style.PALETTE[4],
        "max_files": None,
    },
    {
        "label": "Z' 8000 GeV",
        "dir": "/eos/user/m/masegret/dati_locali/"
               "user.mmarr.mc23_13p6TeV.801866.Py8EG_A14NNPDF23LO_Zp_mm_ZeroWidth8000."
               "MCP_TESTNTUP.mc23e_ANALYSIS.root",
        "color": style.PALETTE[5],
        "max_files": None,
    },
]

N_BINS = 80
X_MIN, X_MAX = 5.0, 20000.0


def build_chain(directory, max_files=None):
    chain = ROOT.TChain(TREE_NAME)
    root_files = sorted(glob.glob(os.path.join(directory, "**", "*.root"), recursive=True))
    if max_files is not None:
        root_files = root_files[:max_files]
    for f in root_files:
        chain.Add(f)
    n_entries = chain.GetEntries()
    print(f"[INFO] {directory}: {len(root_files)} file, {n_entries} entries")
    if n_entries == 0:
        raise RuntimeError(f"Chain vuota per {directory}")
    return chain


def log_binning(n_bins, x_min, x_max):
    import array
    edges = [x_min * (x_max / x_min) ** (i / n_bins) for i in range(n_bins + 1)]
    return array.array('d', edges)


def main():
    edges = log_binning(N_BINS, X_MIN, X_MAX)
    histos = []

    for s in SAMPLES:
        chain = build_chain(s["dir"], s.get("max_files"))
        chain.SetBranchStatus("*", 0)
        chain.SetBranchStatus("muon_pt", 1)

        h = ROOT.TH1F(f"h_pt_{len(histos)}", ";p_{T}^{muon} [GeV];N_{bin}/N_{tot}",
                      N_BINS, edges)
        # NB: SetDirectory(0) va fatto DOPO il Draw, non prima: se lo si
        # stacca dalla direttorio prima, TTree::Draw non lo trova piu' e ne
        # crea un altro con lo stesso nome (quello vero), lasciando questo
        # oggetto vuoto.
        chain.Draw(f"muon_pt/1000. >> {h.GetName()}", "", "goff")
        h.SetDirectory(0)

        if h.Integral() > 0:
            h.Scale(1.0 / h.Integral())
        style.style_histo(h, s["color"])
        h.SetLineWidth(2)
        histos.append({"h": h, "label": s["label"]})

    c = ROOT.TCanvas("c_pt_comparison", "", 1000, 750)
    c.SetLogx()
    c.SetLogy()
    c.SetRightMargin(0.28)

    all_positive = [entry["h"].GetBinContent(i)
                    for entry in histos
                    for i in range(1, entry["h"].GetNbinsX() + 1)
                    if entry["h"].GetBinContent(i) > 0]
    y_max = max(all_positive) * 2.0
    y_min = max(min(all_positive) * 0.5, 1e-6)

    frame = ROOT.TH2F("fr_pt", ";p_{T}^{muon} [GeV];N_{bin}/N_{tot}",
                       100, X_MIN, X_MAX, 100, y_min, y_max)
    frame.Draw()

    # legenda tutta nel margine destro allargato, cosi' non copre mai le curve
    leg = style.make_legend(0.74, 0.58, 0.985, 0.90)
    for entry in histos:
        entry["h"].Draw("HIST SAME")
        leg.AddEntry(entry["h"], entry["label"], "l")
    leg.Draw()

    path = os.path.join(IMAGES_DIR, "plot_pt_Z_Zprime")
    c.SaveAs(f"{path}.png")
    c.SaveAs(f"{path}.pdf")
    print(f"[INFO] Salvato: {path}.png / .pdf")


if __name__ == "__main__":
    main()
