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

# PT_BINS ed ETA_BINS sono IDENTICI ad Allineamento di proposito: e'
# lo stesso identico binning, stessa griglia, stesso metodo (q68) e stesso
# fit -- solo campione diverso (MS-misaligned invece di PerfectAlignment).
# Cosi' i due r2 sono confrontabili direttamente, senza dover scorporare
# quanto della differenza viene dal metodo e quanto dall'allineamento (vedi
# la sistematica "d_metodo" in Allineamento/README.md: non e'
# trascurabile, fra il 15% e il 30% relativo).

TREE_NAME = "AnalysisTree"
MAX_EVENTS = -1

PROMPT_IFF_TYPE = 4

# --------------------------------------------------------------------
# Finestra degli istogrammi
# --------------------------------------------------------------------
# Serve solo a dimensionare l'asse: non entra nel risultato. EXPECTED_R2 e'
# piu' alto che nel nominale (1.2e-4) perche' il disallineamento peggiora
# proprio r2 (e' il termine sensibile all'allineamento, vedi README): con
# la finestra tarata sul nominale qui rischi outflow e bin scartati ad alto
# pT. Se print_window_summary() / il diagnostico di outflow in
# extract_width mostrano ancora troppi bin scartati, alzalo ulteriormente
# -- e' solo dimensionamento, non cambia il risultato.
EXPECTED_R1 = 0.020
EXPECTED_R2 = 4.0e-4
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
# PT_FIT_MAX e MIN_REL_ERR sono ereditati cosi' come sono venuti fuori dal
# fit nominale (vedi Allineamento/README.md, sezione "Il fit
# funziona, ma solo fino a ~800 GeV"): partono da qui perche' e' un punto
# di partenza ragionevole, NON perche' debbano per forza valere anche qui.
# MIN_REL_ERR in particolare e' calibrato in modo che chi2/ndf ~ 1 (con un
# floor uniforme il chi2/ndf scala come 1/floor^2, quindi il floor giusto
# e' quello che ci arriva) -- e la dispersione punto-punto puo' essere
# diversa su un campione disallineato. Da ricontrollare al primo giro con
# dati veri, allo stesso modo in cui e' stato fatto per il nominale.
PT_FIT_MAX = 800.0
MIN_REL_ERR = 0.10

# Range esteso, usato come sistematica sul range del fit (variante 2 in
# analyze.py): quanto cambia r2 se si spinge il fit oltre PT_FIT_MAX.
PT_MAX_VARIANT = 2000.0

OUTPUT_ROOT_FILE = "output_res.root"
