# Risoluzione in p_T e working point loose/medium/tight

Stesso campione di `risoluzione_analysis` (Z→μμ, mc23e, PerfectAlignment),
esteso pero' a 68 file (contro i 30 di `risoluzione_analysis`). La domanda
qui e' un'altra: **la risoluzione in curvatura dipende
dal working point di qualita' del muone**? Vengono confrontati i tre WP
standard ATLAS **Loose**, **Medium**, **Tight** (booleani cumulativi:
`muon_Tight` implica `muon_Medium` implica `muon_Loose`, verificato
sull'ntupla).

A differenza di `risoluzione_analysis`, qui **non** si fa lo split
inclusivo/prompt ne' il binning fine in p_T per la risoluzione: si producono
solo i plot richiesti, la risoluzione inclusiva e le efficienze:

1. **`h_res_wp_overlay`** — le tre distribuzioni di risoluzione in curvatura
   (Loose/Medium/Tight), sovrapposte e normalizzate a densita' (stessa area),
   con l'RMS di ciascuna in legenda.
2. **`efficiency_vs_pt`**, **`efficiency_vs_eta`**, **`efficiency_vs_phi`** —
   l'efficienza del WP in funzione di p_T^truth, eta^truth e phi^truth per
   i tre working point, con errori di Clopper-Pearson (`TEfficiency`). Non
   richiesti esplicitamente ma aggiunti perche' interessanti: eta mostra la
   transizione barrel-endcap e il buco di accettanza a eta~0 (regione dei
   servizi del barrel), phi verifica che non ci siano buchi settoriali.
   Binning uniforme e fine per tutte e tre: 50 bin in [0, 500] GeV per p_T,
   27 bin in [-2.7, 2.7] per eta, 32 bin in [-pi, pi] per phi.

## Definizione di "efficienza" usata qui

Il denominatore **non** e' il numero di muoni truth generati, ma il numero
di muoni **ricostruiti e associati con successo** a un muone truth (stesso
denominatore della risoluzione: `muon_truthmuon_index` valido, p_T reco e
truth > 0). Il numeratore e' il sottoinsieme di questi che soddisfa il WP.

Quindi il plot di efficienza risponde a "di un muone gia' ricostruito, con
che probabilita' soddisfa Loose/Medium/Tight?" — **non** e' un'efficienza di
ricostruzione end-to-end rispetto a tutti i muoni truth generati (per quella
servirebbe un denominatore costruito sulla collezione truth, non su quella
reco).

## Bug incontrato: `vector<char>` in PyROOT

I branch `muon_Loose`, `muon_Medium`, `muon_Tight` sono `vector<char>`.
PyROOT restituisce ogni elemento come stringa Python di un carattere
(es. `'\x00'` o `'\x01'`), e **`bool('\x00')` vale `True` in Python** perche'
e' una stringa non vuota, non il carattere nullo. Un primo giro di test
dava il 100% dei muoni passanti tutti e tre i WP — falso, perche' il flag
non veniva mai interpretato come `False`. Fix in `event_loop.py`: si usa
`ord(flags[j])` invece del valore booleano diretto.

## Binning di `efficiency_vs_pt`: barra orizzontale enorme sull'ultimo punto

Prima versione: il binning in p_T per l'efficienza riusava i `PT_BINS` di
`risoluzione_analysis`, pensati per avere abbastanza statistica per l'RMS
della risoluzione — bin larghi e disomogenei, l'ultimo dei quali va da 120 a
500 GeV. `TEfficiency` disegna come barra orizzontale meta' larghezza del
bin (non un errore statistico), quindi l'ultimo punto aveva una barra da
190 GeV, enorme e fuorviante. Con 160M muoni la statistica non e' un
problema: sostituito con un binning uniforme e fine (50 bin, 10 GeV
ciascuno, [0, 500] GeV) — vedi `PT_RANGE`/`PT_NBINS` in `config.py`, stesso
approccio gia' usato per eta/phi.

## Risultato

Statistica piena (tutti e 68 i file, 347'410'870 muoni ricostruiti e
matchati al truth):

| WP     | Muoni passanti | Efficienza | RMS risoluzione |
|--------|----------------|------------|------------------|
| Loose  | 343'009'434    | 98.7%      | 0.0282           |
| Medium | 339'503'110    | 97.7%      | 0.0282           |
| Tight  | 314'169'451    | 90.4%      | 0.0259           |

Il plot overlay mostra le tre distribuzioni di risoluzione praticamente
sovrapposte, con errori ormai trascurabili: **la risoluzione in p_T non
dipende dalla scelta del working point**, che invece sposta in modo netto
l'efficienza. Ha senso fisicamente: il WP seleziona sulla qualita'/tipo del
match (hit nelle camere, chi2, ecc.), non modifica la misura del momento del
muone una volta che questo e' gia' classificato come combined muon.

`efficiency_vs_eta` mostra un calo netto a eta~0 per Medium (~0.71) e Tight
(~0.60), molto meno marcato per Loose: e' il buco di accettanza dovuto ai
servizi nella regione centrale del barrel, atteso in ATLAS. Loose lo sente
meno perche' include anche muoni segment-tagged e calo-tagged, che non
richiedono piena copertura dello spettrometro. `phi` e' piatto come atteso,
nessun buco settoriale evidente. `efficiency_vs_pt` cresce leggermente con
p_T per Tight, plateau gia' raggiunto per Loose/Medium.

Numeri e plot definitivi, statistica piena — pronti per la tesi.

## Come lanciare

Stessa pipeline HTCondor di `risoluzione_analysis` (vedi quel README per il
dettaglio dei comandi), puntata sullo stesso dataset Z→μμ:

```bash
cd ~/TesiMagistrale/risoluzione_analysis/WP

grep MAX_EVENTS config.py        # deve essere -1 per girare su tutto
./gen_jobs.sh                    # crea jobs/do_0.sh ... do_29.sh + files.txt
condor_submit condorSub.sub

# quando condor_q e' vuoto:
python3 merge.py /eos/user/m/masegret/wp_out
```

Output: `output_wp.root` (istogrammi di risoluzione, pass/total per WP in
p_T/eta/phi, `TEfficiency`) e
`images/{h_res_wp_overlay,efficiency_vs_pt,efficiency_vs_eta,efficiency_vs_phi}.{png,pdf}`.

## I file

Stessa struttura di `risoluzione_analysis`: `chain_builder.py` e `style.py`
sono identici (copiati cosi' come sono). Cambiano `config.py` (WP invece di
bin p_T come oggetto principale, niente `truthmuon_IFFType`/prompt, binning
eta/phi), `histograms.py` (un istogramma di risoluzione per WP + pass/total
in p_T/eta/phi per le efficienze, tramite un dizionario `_EFF_VARS` cosi' da
non triplicare il codice), `event_loop.py`, `plotting.py` (i plot sopra,
`draw_efficiency` generalizzata sulla variabile) e `main.py`/`merge.py` di
conseguenza.
