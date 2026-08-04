"""
Configurazione dell'analisi: RMS della risoluzione in p_T vs |eta_truth|,
per ciascun bin di p_T (selezione combinata pT + eta richiesta da Marco).

Bin edges in eta come discusso con Luca in chat:
0.0-0.1   -> muoni calo-tagged/segment-tagged, risoluzione peggiore
0.1-1.01  -> barrel, poco multiple scattering, buona B x L
1.01-1.3  -> regione di transizione barrel/endcap
1.3-1.7   -> inversioni di campo, risoluzione peggiore
1.7-2.5   -> endcap, shielding davanti alla prima camera
2.5-2.8   -> endcap senza inner detector, solo tracce stand-alone
"""

PT_BINS = [
    {"name": "20_30", "min": 20, "max": 30},
    {"name": "30_40", "min": 30, "max": 40},
    {"name": "40_50", "min": 40, "max": 50},
    {"name": "50_80", "min": 50, "max": 80},
    {"name": "80_120", "min": 80, "max": 120},
    {"name": "120_500", "min": 120, "max": 500},
]

ETA_BINS = [
    {"min": 0.0, "max": 0.1},
    {"min": 0.1, "max": 1.01},
    {"min": 1.01, "max": 1.3},
    {"min": 1.3, "max": 1.7},
    {"min": 1.7, "max": 2.5},
    {"min": 2.5, "max": 2.8},
]

TREE_NAME = "AnalysisTree"
MAX_EVENTS = -1 # -1 = nessun limite, processa l'intero dataset

# Selezione sui soli muoni truth "prompt", come nell'altra analisi
PROMPT_IFF_TYPE = 4
