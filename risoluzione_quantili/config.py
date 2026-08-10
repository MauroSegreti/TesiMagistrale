PT_BINS = [
    {"name": "20_30", "min": 20, "max": 30, "mean": 25.0},
    {"name": "30_40", "min": 30, "max": 40, "mean": 35.0},
    {"name": "40_50", "min": 40, "max": 50, "mean": 45.0},
    {"name": "50_70", "min": 50, "max": 70, "mean": 60.0},
    {"name": "70_100", "min": 70, "max": 100, "mean": 85.0},
    {"name": "100_150", "min": 100, "max": 150, "mean": 125.0},
    {"name": "150_200", "min": 150, "max": 200, "mean": 175.0},
    {"name": "200_300", "min": 200, "max": 300, "mean": 250.0},
    {"name": "300_500", "min": 300, "max": 500, "mean": 400.0},
    {"name": "500_800", "min": 500, "max": 800, "mean": 650.0},
    {"name": "800_1200", "min": 800, "max": 1200, "mean": 1000.0},
    {"name": "1200_1750", "min": 1200, "max": 1750, "mean": 1475.0},
    {"name": "1750_2500", "min": 1750, "max": 2500, "mean": 2125.0},
    {"name": "2500_3000", "min": 2500, "max": 3000, "mean": 2750.0},
    {"name": "3000_4000", "min": 3000, "max": 4000, "mean": 3500.0},
    {"name": "4000_6000", "min": 4000, "max": 6000, "mean": 5000.0},
]

ETA_BINS = [
    {"min": 0.0, "max": 0.1, "label": "0.0 #leq |#eta| < 0.1"},
    {"min": 0.1, "max": 1.05, "label": "0.1 #leq |#eta| < 1.05"},
    {"min": 1.05, "max": 1.3, "label": "1.05 #leq |#eta| < 1.3"},
    {"min": 1.3, "max": 1.7, "label": "1.3 #leq |#eta| < 1.7"},
    {"min": 1.7, "max": 2.5, "label": "1.7 #leq |#eta| < 2.5"},
    {"min": 2.5, "max": 2.8, "label": "2.5 #leq |#eta| < 2.8"},
]

TREE_NAME = "AnalysisTree"
MAX_EVENTS = -1

PROMPT_IFF_TYPE = 4

# Nessun taglio artificiale sul pT truth: i bin arrivano fin dove c'e'
# statistica. Il vecchio PT_TRUTH_MAX = 3000 buttava via i muoni del Z' da
# 8 TeV, che stanno intorno ai 4 TeV.

# --------------------------------------------------------------------
# Finestra degli istogrammi
# --------------------------------------------------------------------
# Serve solo a dimensionare l'asse: non entra nel risultato. Tarata sui
# valori misurati nel primo giro (r1 ~ 0.02, r2 ~ 1e-4).
EXPECTED_R1 = 0.020
EXPECTED_R2 = 1.2e-4
N_WINDOW_SIGMA = 6.0
MIN_WINDOW = 0.12
HIST_N_BINS = 400

# Allargamento per bin di eta: ad alto |eta| le tracce sono stand-alone
# (niente inner detector oltre 2.5) e le code sono molto piu' larghe.
ETA_WINDOW_SCALE = [1.0, 1.0, 1.0, 1.5, 1.5, 4.0]

MIN_ENTRIES_FOR_FIT = 200

PLOT_X_MIN = 15
PLOT_X_MAX = 6000

# --------------------------------------------------------------------
# Fit della formula a 3 termini su sigma_68(pT)
# --------------------------------------------------------------------
# Sul range completo il fit non converge bene (chi2/ndf fino a 10^4-10^5,
# residui fino al 50%): con decine di milioni di entries per bin l'errore
# statistico su sigma_68 e' cosi' piccolo che il chi2 e' dominato da
# deviazioni sub-percento, e la formula smette comunque di descrivere i
# dati oltre qualche centinaio di GeV, dove le code non gaussiane (vedi
# asimmetria e q68/gaus in inspect_bins.py) rendono sigma_68 non piu' un
# singolo parametro di scala pulito.
#
# PT_FIT_MAX: range nominale del fit, tarato empiricamente (vedi
# scratchpad/explore_fit.py) come il punto oltre cui il chi2/ndf peggiora
# in modo monotono e netto.
# MIN_REL_ERR: floor sistematico sull'errore di sigma_68 prima del fit,
# sigma_err = max(sigma_err_stat, MIN_REL_ERR * sigma). Con un floor
# relativo uniforme il chi2/ndf scala come 1/MIN_REL_ERR^2 (i parametri
# migliori non cambiano, cambia solo il peso assoluto del disaccordo), quindi
# il valore non e' arbitrario: 0.10 e' calibrato in modo che chi2/ndf ~ 1
# entro PT_FIT_MAX per la maggior parte dei bin di eta -- cioe' e' la
# sistematica intrinseca misurata della parametrizzazione a 3 parametri, non
# un numero scelto per far tornare il fit.
PT_FIT_MAX = 800.0
MIN_REL_ERR = 0.10

# Range esteso, usato come sistematica sul range del fit (variante 2 in
# analyze.py): quanto cambia r2 se si spinge il fit oltre PT_FIT_MAX.
PT_MAX_VARIANT = 2000.0

OUTPUT_ROOT_FILE = "output_res.root"
