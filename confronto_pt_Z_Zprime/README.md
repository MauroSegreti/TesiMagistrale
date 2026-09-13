# Confronto p_T dei muoni: Z vs Z'

Plot rapido (non un framework a job HTCondor come le altre cartelle) che
sovrappone la distribuzione del $p_T$ dei muoni **ricostruiti** (branch
`muon_pt`, nessun taglio, nessun match al truth) nel campione Z e in
**cinque** campioni Z' a diversa massa, per far vedere a colpo d'occhio come
lo spettro si sposta verso $p_T$ sempre piu' alti al crescere della massa
della risonanza.

## File

- **`style.py`** — stile ATLAS-like, copiato identico dalle altre analisi.
- **`plot_pt_comparison.py`** — legge i campioni, riempie un istogramma per
  campione, normalizza e sovrappone tutto in un unico plot log-log.
- **`images/plot_pt_Z_Zprime.png` / `.pdf`** — il risultato.

Uso: `python3 plot_pt_comparison.py` (serve l'ambiente ROOT: `setupATLAS;
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"`).

## Campioni usati

| Campione | DSID | File usati | Note |
|---|---|---|---|
| Z #rightarrow #mu#mu | 601190 | 20 dei 68 disponibili in `PerfectAlignment/` | vedi sotto |
| Z' 500 GeV | 801862 | 1/1 | `dati_locali/` |
| Z' 1000 GeV | 801863 | 1/1 | `dati_locali/` |
| Z' 3000 GeV | 801864 | 1/1 | `dati_locali/` |
| Z' 5000 GeV | 801865 | 1/1 | `dati_locali/` — v. nota sull'esclusione sotto |
| Z' 8000 GeV | 801866 | 1/1 | `dati_locali/` |

**Perche' solo 20 file su 68 per Z:** leggere l'intero campione (~100M eventi)
interattivamente e' lento (stesso problema documentato in
`risoluzione_analysis/README.md`, che infatti gira via HTCondor). Qui basta la
*forma* della distribuzione per un plot qualitativo, e 20 file (~31M muoni)
sono piu' che sufficienti per una curva liscia — non serve la statistica
piena.

**5000 e 8000 GeV, come sono stati aggiunti:** ci sono in realta' **5** punti
di massa Z' prodotti (500/1000/3000/5000/8000 GeV, DSID 801862-801866).
Inizialmente solo i primi tre erano scaricati in locale:
- il punto **5000 GeV** risultava esplicitamente **escluso dall'analisi** nel
  README top-level (cartella dedicata `samples_esclusi/`, inizialmente non me lo faceva scarica);
- il punto **8000 GeV** non era mai stato scaricato (solo il `.txt` con l'URL
  XRootD, stesso motivo).

Un tentativo di lettura diretta via XRootD (`root://grid-dc.t2.mpcdf.mpg.de:
1094//...`, senza scaricare) e' rimasto bloccato — porta 1094 non
raggiungibile in uscita da questo nodo. Con la voms-proxy attiva
(`voms-proxy-init -voms atlas`) e' bastato invece un vero
`rucio download --rse MPPMU_PERF-MUONS <scope>:<dataset>`: rucio ha scelto in
automatico il protocollo **davs** (WebDAV, porta 2880) invece di xrootd, che
da questo nodo funziona (~300 MB scaricati in ~5 secondi ciascuno). File
copiati in `dati_locali/` con la stessa convenzione di naming degli altri tre
campioni Z'.

Su richiesta esplicita e' stato incluso anche il 5000 GeV nonostante la nota
di esclusione trovata nel README top-level — **il motivo dell'esclusione
originale resta pero' non chiarito**: da verificare prima di usare questo
punto per conclusioni quantitative in tesi (potrebbe essere stato escluso per
un problema di produzione/statistica non evidente da un plot di sola forma
come questo).

## Asse Y: cosa significa "N_bin/N_tot"

Ogni istogramma e' normalizzato al proprio integrale
(`h.Scale(1.0/h.Integral())`), **non** e' il conteggio grezzo (`Entries`).
Il valore in ogni bin e' quindi la frazione di muoni di quel campione che
cade in quel bin di $p_T$: $N_{bin}/N_{tot}$. Serve a confrontare la *forma*
delle sei distribuzioni indipendentemente dal numero di muoni in ciascun
campione (che varia di ordini di grandezza: ~31M per Z contro ~250k per
ogni Z').

## Il simbolo "infinito" nella legenda (Z)

Non era un bug del plot: era **"#mu#mu"** (due lettere greche mu scritte una
attaccata all'altra per Z #rightarrow #mu#mu) che, alla dimensione di testo
piccola della legenda, si fondono visivamente in qualcosa che assomiglia a un
simbolo di infinito. Corretto usando `#mu^{+}#mu^{-}` (mu con le cariche
esplicite): oltre a separare visivamente i due simboli, e' anche la notazione
fisica standard per il decadimento in una coppia muone-antimuone. Verificato
aprendo sia il `.png` che il `.pdf` prodotti: il simbolo ora si legge
correttamente come $\mu^+\mu^-$.

## Il "picco" al bordo sinistro del plot (~5 GeV)

Non e' un picco fisico, e' un artefatto del taglio del plot. Lo spettro
*reale* di `muon_pt` (controllato in bin fini da 0.5 GeV su Z' 500 GeV) ha un
taglio netto esattamente a **2.5 GeV** (zero entries sotto, poi caduta
ripidissima sopra):

```
 2.00 -  2.50 GeV : 0
 2.50 -  3.00 GeV : 38719
 3.00 -  3.50 GeV : 23307
 3.50 -  4.00 GeV : 14057
 4.00 -  4.50 GeV : 8970
 4.50 -  5.00 GeV : 5917
 5.00 -  5.50 GeV : 13083   <- qui inizia il plot (X_MIN = 5 GeV)
 5.50 -  6.00 GeV : 8582
 ...
```

Il taglio a 2.5 GeV e' verosimilmente una selezione minima di $p_T$ applicata
in produzione dell'ntupla (soglia tipica di ricostruzione muone). Il plot
attuale parte da $p_T = 5$ GeV, cioe' **dentro** la parte ancora ripidamente
decrescente di questo spettro a bassa statistica combinatoria — per questo il
primo bin visibile sembra "risalire": in realta' sta solo mostrando la coda
discendente di una feature che ha il suo massimo vero appena sotto il bordo
del plot, fuori dall'intervallo mostrato. Non e' legato in alcun modo alle
risonanze Z/Z' (che vivono a $p_T \gg 5$ GeV).

## Range esteso a 20 TeV: le code a destra erano tagliate

Versione iniziale del plot: `X_MAX = 6000` GeV. A quel range, le code destre
di Z' 3000/5000/8000 GeV **non erano ancora scese verso lo zero** quando
arrivavano al bordo del frame — non un effetto ottico, verificato sui conteggi
grezzi (bin di overflow oltre 6000 GeV rispetto al totale del campione):

| Campione | overflow oltre 6000 GeV | frazione del campione |
|---|---:|---:|
| Z' 3000 GeV | 1243 | 0.5% |
| Z' 5000 GeV | 4649 | 1.9% |
| Z' 8000 GeV | 19552 | **7.8%** |

Per l'8000 GeV in particolare l'ultimo bin visibile prima del taglio aveva
ancora contenuto **crescente** avvicinandosi al bordo (curva non ancora
scesa dal picco). Portato `X_MAX` a **20000 GeV** (e i bin da 70 a 80, per
mantenere una risoluzione simile): ora tutte e sei le code scendono
visibilmente prima del bordo destro.

Non ho spinto oltre i 20 TeV nonostante resti un overflow piccolo ma non
nullo anche li' (fino all'1.2% per l'8000 GeV): la coda continua molto oltre
20 TeV per **tutti** i campioni, compreso Z (che a rigore non dovrebbe avere
muoni fisici a quel $p_T$) — e' la coda di mismisura tipica dello
spettrometro a muoni ad alto $p_T$ (il termine risolutivo $b \times p_T$
discusso in `risoluzione_analysis/README.md`: a $p_T$ molto alti basta un
piccolo errore sulla sagitta per dare un $p_T$ ricostruito enormemente
sballato), non una coda fisica del decadimento. Andare oltre 20 TeV
comprimerebbe inutilmente i picchi (che vivono tutti sotto i 3.3 TeV) per
inseguire una coda che non converge comunque entro un range ragionevole.

## Picchi attesi (per la descrizione del plot in tesi)

Ogni curva picca a circa **meta' della massa** della risonanza di origine —
cinematica di un decadimento a due corpi a riposo, $p_T^{\mu} \approx M/2$:

| Campione | Massa risonanza | $p_T$ atteso (M/2) | $p_T$ osservato (bin del massimo) |
|---|---:|---:|---:|
| Z #rightarrow #mu^{+}#mu^{-} | 91.2 GeV | ~45 GeV | ~42 GeV (40-44) |
| Z' 500 GeV | 500 GeV | 250 GeV | ~244 GeV (232-257) |
| Z' 1000 GeV | 1000 GeV | 500 GeV | ~455 GeV (432-479) |
| Z' 3000 GeV | 3000 GeV | 1500 GeV | ~1284 GeV (1217-1350) |
| Z' 5000 GeV | 5000 GeV | 2500 GeV | ~2156 GeV (2044-2267) |
| Z' 8000 GeV | 8000 GeV | 4000 GeV | ~3263 GeV (3094-3432) |

(colonna destra: centro del bin con il massimo, con l'intervallo del bin tra
parentesi — binning log con 80 bin tra 5 e 20000 GeV, quindi i bin sono
larghi specialmente ad alto $p_T$; per un valore piu' preciso servirebbe un
fit invece del solo bin piu' popolato.)

(Il leggero scarto per Z, ~42 invece di ~45 GeV, e' dovuto al boost del
bosone e alla richiesta implicita che entrambi i muoni siano ricostruiti —
non e' un errore del plot.)

## Da fare

- Chiarire il motivo originale dell'esclusione del campione Z' 5000 GeV
  (`samples_esclusi/` nel top-level) prima di usarlo per conclusioni
  quantitative — qui e' incluso solo per il confronto di forma su richiesta
  esplicita, il dubbio sull'esclusione non e' stato risolto.
- Lo scarto tra $p_T$ atteso (M/2) e osservato cresce con la massa (~7% per
  Z, ~14% per Z' 3000/5000, ~18% per Z' 8000 GeV): da capire se e' solo
  binning grossolano ad alto $p_T$ o un effetto fisico/di accettanza reale,
  se questo plot deve essere usato per altro che un confronto qualitativo di
  forma.
