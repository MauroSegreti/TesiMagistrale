"""
Configurazione centralizzata dell'analisi.
Modifica qui il binning in pT o le altre costanti: tutto il resto del
progetto le legge da questo file, così non serve toccare il codice
in più punti.
"""

PT_BINS = [
    {"name": "0_20", "min": 0, "max": 20, "x_center": 10, "x_err": 10},
    {"name": "20_30", "min": 20, "max": 30, "x_center": 25, "x_err": 5},
    {"name": "30_40", "min": 30, "max": 40, "x_center": 35, "x_err": 5},
    {"name": "40_50", "min": 40, "max": 50, "x_center": 45, "x_err": 5},
    {"name": "50_80", "min": 50, "max": 80, "x_center": 65, "x_err": 15},
    {"name": "80_120", "min": 80, "max": 120, "x_center": 100, "x_err": 20},
    {"name": "120_500", "min": 120, "max": 500, "x_center": 310, "x_err": 190},
]

TREE_NAME = "AnalysisTree"
MAX_EVENTS = 2_000_000

# truthmuon_IFFType == 4 corrisponde a "PromptMuon" (vedi tabella IFFType
# condivisa da Luca): i muoni truth "prompt" richiesti come selezione extra.
PROMPT_IFF_TYPE = 4

OUTPUT_ROOT_FILE = "output_risoluzione.root"
