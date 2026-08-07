# Analisi risoluzione in pT dei muoni

Misura la risoluzione in curvatura dei muoni ricostruiti confrontandoli con i
corrispondenti muoni truth, inclusivamente e in bin di pT truth.

## Come si lancia

```bash
python3 main.py /eos/user/m/masegret/PerfectAlignment/user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu.MCP_TESTNTUP.mc23e_ANALYSIS.root
```


## Cosa produce

- `output_risoluzione.root` — tutti gli istogrammi e i due `TGraphErrors`
- `images/h_res_all.png|.pdf` — istogramma inclusivo
- `images/plot_range_<bin>.png|.pdf` — un plot per ciascun bin di pT
- `images/plot_bins_overlay.png|.pdf` — tutti i bin sovrapposti, normalizzati ad
  area unitaria (confronta le *forme*, non i conteggi)
- `images/rms_vs_pt.png|.pdf` — RMS vs pT truth

Ognuno di questi esiste anche in versione `_prompt`, ottenuta selezionando solo
i muoni truth con `truthmuon_IFFType == 4`.

## La grandezza misurata

Per ogni muone reco con un match truth valido:

```
res = (1/pT_reco - 1/pT_truth) / (1/pT_truth) = pT_truth/pT_reco - 1
```

È la risoluzione in **curvatura** (1/pT), la variabile naturale per lo studio
dell'allineamento: gli effetti di misalignment sono uno shift additivo in 1/pT.
I pT nella ntupla sono in MeV, il codice divide per 1000 e lavora in GeV.

---

## Struttura dei file

### `config.py`

Solo costanti — è l'unico file da toccare per cambiare la configurazione.

| `PT_BINS` | Lista dei bin di pT. Ogni voce ha `name` (usato nei nomi degli istogrammi e dei file), 
`min`/`max` (estremi in GeV, intervallo chiuso a sinistra e aperto a destra), 
`x_center`/`x_err` (punto e barra orizzontale nel grafico RMS vs pT). 

| `TREE_NAME` | Nome del TTree dentro i file ROOT (`AnalysisTree`). 

| `MAX_EVENTS` | Limite di eventi. `-1` = tutti. Mettilo a `100000` per un test rapido prima del run completo. |
| `PROMPT_IFF_TYPE` | Valore di `truthmuon_IFFType` corrispondente ai muoni prompt (`4`). 
| `ACTIVE_BRANCHES` | I soli branch letti dal disco. Serve a non decomprimere l'intera ntupla a ogni evento. 
| `OUTPUT_ROOT_FILE`, `IMAGES_DIR` | Nomi di output. |

### `chain_builder.py` — I/O

**`build_chain(tree_name, path)`**
Costruisce e restituisce la `TChain`. Riconosce i tre tipi di input descritti
sopra. Stampa quanti file ha aggiunto e il totale di entries; solleva un errore
se la chain risulta vuota, così un path sbagliato o un nome di tree errato si
manifesta subito invece di produrre istogrammi vuoti dopo ore di run.

**`enable_branches(chain, branches)`**
Disattiva tutti i branch e riattiva solo quelli in `ACTIVE_BRANCHES`. Con ntuple
larghe questo è il singolo fattore che più incide sul tempo di esecuzione: ROOT
legge e decomprime solo le colonne che servono davvero.

### `histograms.py` — definizione degli istogrammi

**`make_resolution_histo(name, title_prefix)`**
Crea un `TH1F` con il binning standard della risoluzione: 100 bin tra -0.2 e
+0.2. `SetDirectory(0)` scollega l'istogramma dal file ROOT corrente, così
l'ordine in cui apri il `TFile` non può farteli sparire.

**`build_histogram_set(suffix="")`**
Restituisce la coppia `(h_all, histos_pt)`: l'istogramma inclusivo e un
dizionario `{nome_bin: TH1F}` con un istogramma per ciascun bin di `PT_BINS`.
Il `suffix` genera in un colpo solo il set parallelo per la selezione prompt
(`""` → inclusivo, `"_prompt"` → prompt), evitando di duplicare il codice.

### `event_loop.py` — il loop

**`_find_bin(pt_truth)`**
Restituisce il nome del bin di pT che contiene `pt_truth`, oppure `None` se il
valore cade fuori dall'ultimo bin (sopra 500 GeV). Funzione ausiliaria: prima
questa ricerca era duplicata per l'inclusivo e per il prompt.

**`process_events(chain, h_all, histos_pt, h_all_prompt, histos_pt_prompt)`**
Il cuore dell'analisi. Per ogni evento:

1. legge i quattro branch necessari;
2. per ogni muone reco `j` recupera l'indice del truth associato da
   `muon_truthmuon_index[j]`;
3. **scarta** i muoni con indice negativo (nessun match truth) o fuori range —
   questo è il taglio principale di qualità;
4. converte in GeV e scarta i pT non positivi;
5. calcola `res` e riempie l'istogramma inclusivo più quello del bin di pT;
6. se `truthmuon_IFFType[idx_truth] == 4` riempie anche il set prompt.

Restituisce `(filled_muons, filled_muons_prompt)`, i contatori di muoni
effettivamente usati — utile come sanity check: il rapporto prompt/inclusivo su
un campione Z→μμ deve essere alto (i muoni non-prompt sono contaminazione da
decadimenti in volo, heavy flavour, fake).

Progresso stampato ogni 100k eventi con `flush=True`, così la barra si aggiorna
anche quando l'output è rediretto su file in batch.

### `plotting.py` — disegno e salvataggio

**`make_rms_graph(histos_pt, name, title)`**
Estrae `GetRMS()` e `GetRMSError()` da ciascun istogramma di bin e li impacchetta
in un `TGraphErrors`: punti in `x_center`, barre orizzontali `x_err` (larghezza
del bin), barre verticali dall'errore sull'RMS. È il plot finale della
risoluzione in funzione del pT.

**`_save(canvas, basename)`**
Salva ogni canvas in `images/` sia in PNG (per condividere) sia in PDF
(vettoriale, per tesi e paper). Crea la cartella se non esiste.

**`draw_inclusive(h_all, suffix)`**
Istogramma inclusivo riempito, con legenda che riporta entries, media e RMS.

**`draw_single_bins(histos_pt, suffix)`**
Un file per bin di pT, con entries e RMS in legenda.

**`draw_bins_overlay(histos_pt, suffix)`**
Tutti i bin nello stesso canvas con colori distinti, normalizzati ad area
unitaria per confrontarne la larghezza. Lavora su **cloni** degli istogrammi:
la normalizzazione non tocca gli originali, quindi il file ROOT e gli altri plot
conservano i conteggi assoluti.

**`draw_rms_graph(graph, suffix)`**
Il grafico RMS vs pT, con griglia.

**`save_all_plots(h_all, histos_pt, graph, suffix)`**
Chiama le quattro funzioni sopra nell'ordine giusto (i singoli bin prima
dell'overlay).

### `style.py` — estetica

**`PALETTE`**
Sette colori scelti per restare distinguibili anche stampati in bianco e nero.

**`apply_style()`**
Definisce e applica globalmente un `TStyle` in stile ATLAS: font Helvetica (42),
tick su tutti e quattro i lati, niente stat box né titolo automatico, margini
generosi per le label degli assi, linee spesse. Attiva anche la **batch mode**,
necessaria per girare su lxplus senza display X11. Va chiamata una volta sola in
cima a `main.py`, prima di creare qualunque canvas.

**`style_histo(h, color, fill=False)`**
Applica colore e spessore linea a un istogramma; con `fill=True` aggiunge un
riempimento semitrasparente.

**`make_legend(x1, y1, x2, y2)`**
Legenda senza bordo né sfondo, con font e dimensioni coerenti col resto.

### `main.py` — orchestrazione

Nell'ordine: applica lo stile, costruisce i due set di istogrammi, apre la chain
e limita i branch, lancia il loop, costruisce i due grafici RMS, scrive tutto
nel file ROOT, genera i plot, stampa il riassunto.

---

## Modifiche rispetto alla versione precedente

1. **Input `.txt` (bug bloccante).** `build_chain` gestiva solo path terminanti
   in `.root` o cartelle: con il file lista che stai usando la chain sarebbe
   rimasta vuota e avresti ottenuto istogrammi a zero entries senza alcun
   errore. Ora legge le liste, e in più fallisce esplicitamente se la chain è
   vuota.
2. **Batch mode.** Senza `SetBatch(True)` il job prova ad aprire finestre X11 e
   su lxplus/condor si pianta o rallenta parecchio.
3. **Overlay non distruttivo.** `draw_bins_overlay` normalizzava gli istogrammi
   *reali*: i plot dei singoli bin, disegnati dopo, mostravano un asse Y
   normalizzato con l'etichetta "Muoni / bin". Ora lavora su cloni.
4. **Scrittura prima del disegno** in `main.py`, per la stessa ragione.
5. **Lettura selettiva dei branch**, per il tempo di esecuzione.
6. Rimosso un loop vuoto senza effetto in `style.py`; deduplicata la ricerca del
   bin di pT in `event_loop.py`.

## Prima del run completo

37M eventi con un loop Python su `TChain` sono lenti (ordine di ore). Consigli:

- prova prima con `MAX_EVENTS = 100000` in `config.py` e controlla che i
  contatori finali non siano zero;
- lancia il run completo dentro `tmux`/`screen`, o su HTCondor, non da sessione
  SSH interattiva;
- se i tempi restano proibitivi, la stessa analisi si riscrive in `RDataFrame`
  (loop compilato + multithreading) con un guadagno di uno o due ordini di
  grandezza.
