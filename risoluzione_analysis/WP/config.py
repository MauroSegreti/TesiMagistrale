import math

# binning per le efficienze vs pT/eta/phi: uniforme e fine per tutte e tre.
# I PT_BINS larghi e disomogenei di risoluzione_analysis (pensati per avere
# abbastanza statistica per l'RMS) qui non servono: con 160M muoni la
# statistica non e' un problema, e un binning uniforme evita che TEfficiency
# disegni la barra orizzontale (= mezza larghezza del bin, non un errore)
# enorme sull'ultimo bin 120-500 GeV com'era in origine.
PT_RANGE = (0, 500)
PT_NBINS = 50

ETA_RANGE = (-2.7, 2.7)
ETA_NBINS = 27

PHI_RANGE = (-math.pi, math.pi)
PHI_NBINS = 32

TREE_NAME = "AnalysisTree"

MAX_EVENTS = -1

# Working point loose/medium/tight: flag booleani cumulativi (muon_Tight
# implica muon_Medium implica muon_Loose), verificato sull'ntupla.
WP_LIST = ["Loose", "Medium", "Tight"]
WP_BRANCH = {
    "Loose": "muon_Loose",
    "Medium": "muon_Medium",
    "Tight": "muon_Tight",
}
ACTIVE_BRANCHES = [
    "muon_pt",
    "truthmuon_pt",
    "truthmuon_eta",
    "truthmuon_phi",
    "muon_truthmuon_index",
    "muon_Loose",
    "muon_Medium",
    "muon_Tight",
]

OUTPUT_ROOT_FILE = "output_wp.root"
IMAGES_DIR = "images"
