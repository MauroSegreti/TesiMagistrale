# Risoluzione in $p_T$ dei muoni — Z→μμ

Misuro la risoluzione in $p_T$ dei muoni confrontando il $p_T$ ricostruito con
quello a livello di truth, su un campione MC di Z→μμ (mc23e, PerfectAlignment).

La variabile che studio è la risoluzione in curvatura:

$$\frac{1/p_T^{reco} - 1/p_T^{truth}}{1/p_T^{truth}} = \frac{p_T^{truth}}{p_T^{reco}} - 1$$

La riempio in 7 bin di $p_T^{truth}$ (0-20, 20-30, 30-40, 40-50, 50-80, 80-120,
120-500 GeV) e prendo l'RMS di ogni distribuzione come stima della risoluzione.
Tutto viene fatto due volte: una inclusiva e una sui soli muoni **prompt**
(`truthmuon_IFFType == 4`).

## Il problema: 100M di eventi

Il dataset sono 30 file per un totale di circa 100 milioni di eventi. Girando
`main.py` in interattivo su lxplus il job crashava: le sessioni interattive
vengono uccise (limite di tempo, memoria, o connessione che cade). Dopo una
notte intera ero arrivato a ~50M eventi e poi ho perso tutto.

## La soluzione: HTCondor

Su consiglio di Luca sono passato alle code batch di HTCondor. Invece di un
processo unico che macina 100M eventi in serie, lancio **30 job in parallelo**,
uno per file di input, che girano su macchine diverse e sono completamente
staccati dalla mia sessione — posso chiudere il terminale e tornare il giorno
dopo.

Il guadagno è sostanziale: da una notte intera (senza nemmeno arrivare in fondo)
a circa **mezz'ora**, perché ogni job vede solo ~3.3M eventi invece di 100M.
Alla fine unisco gli output con `hadd`.

## Comandi principali

Setup dell'ambiente, per accedere ai dataset con rucio:

```bash
setupATLAS
voms-proxy-init -voms atlas
lsetup rucio
```

Il setup di ROOT non lo faccio a mano: sta dentro gli script generati da
`gen_jobs.sh`, così ogni job di condor se lo fa da solo sulla macchina su cui
gira (`lsetup "root 6.40.02-x86_64-el9-gcc15-opt"`, la stessa versione che uso
in interattivo).

Generazione degli script di job e submit:

```bash
cd ~/TesiMagistrale/risoluzione_analysis

grep MAX_EVENTS config.py        # deve essere -1 per girare su tutto
./gen_jobs.sh                    # crea jobs/do_0.sh ... do_29.sh + files.txt
condor_submit condorSub.sub      # 30 job
```

Monitoraggio:

```bash
condor_q                         # IDLE = in coda, RUN = in esecuzione
watch -n 30 condor_q             # aggiorna da solo
tail -f logs/do_0.sh.out         # progresso di un singolo job
condor_q -hold                   # perché un job è in stato held
```

Prima del submit completo conviene provare **un solo job**, molto più rapido da
debuggare:

```bash
sed 's|jobs/do_\*.sh|jobs/do_0.sh|' condorSub.sub > condorTest.sub
condor_submit condorTest.sub
cat logs/do_0.sh.err
```

Merge e plot finali, quando `condor_q` è vuoto:

```bash
ls -d /eos/user/m/masegret/risoluzione_out/job_*/output_risoluzione.root | wc -l   # 30
grep -l Traceback logs/*.err                                                       # nulla
python3 merge.py /eos/user/m/masegret/risoluzione_out
```

Per guardare i PNG dal browser li copio su EOS e li apro da
[cernbox.cern.ch](https://cernbox.cern.ch):

```bash
cp -r images output_risoluzione.root /eos/user/m/masegret/risoluzione_out/
```

## I file

**`config.py`** — tutti i parametri in un posto solo: definizione dei bin di
$p_T$, nome del TTree (`AnalysisTree`), `MAX_EVENTS` (a `-1` per girare su tutto,
un valore positivo per i test rapidi), i branch da attivare e i nomi degli
output.

**`chain_builder.py`** — costruisce la `TChain` a partire da una directory, da
una lista `.txt` o da un singolo file `.root`. Il controllo sulla directory
viene prima di quello sull'estensione, perché le directory create da rucio si
chiamano anche loro `*.ANALYSIS.root`. Attiva solo i branch che servono, così
non legge dal disco roba inutile.

**`histograms.py`** — crea gli istogrammi di risoluzione (100 bin tra -0.2 e
0.2): uno inclusivo più uno per ciascun bin di $p_T$, in due set separati per
inclusivo e prompt.

**`event_loop.py`** — il loop sugli eventi. Per ogni muone ricostruito segue
`muon_truthmuon_index` per risalire al muone truth associato, scarta i match non
validi, calcola la risoluzione e riempie l'istogramma inclusivo, quello del bin
di appartenenza e, se `IFFType == 4`, i corrispondenti prompt.

**`plotting.py`** — costruisce il `TGraphErrors` di RMS vs $p_T$ e salva tutti i
plot in PNG e PDF: distribuzione inclusiva, un plot per bin, l'overlay
normalizzato di tutti i bin e il grafico finale della risoluzione.
`draw_prompt_vs_inclusive` produce inoltre l'overlay diretto tra `h_res_all`
e `h_res_all_prompt` (normalizzati a densità, con RMS ed entries in legenda),
usato per giustificare lo split inclusivo/prompt — vedi "Inclusivo vs prompt"
più sotto.

**`style.py`** — stile ATLAS-like (font, margini, tick su tutti i lati, niente
box delle statistiche) e la palette di colori usata nell'overlay.

**`main.py`** — mette insieme tutto: costruisce la chain, gira il loop, salva
istogrammi e grafici nel `.root` e produce le immagini. È quello che lancia ogni
job di condor, su un file alla volta.

**`gen_jobs.sh`** — genera uno script `jobs/do_N.sh` per ogni file di input. Ogni
script fa il setup di ATLAS/ROOT, imposta il `PYTHONPATH` sulla directory di
analisi e lancia `main.py` dentro una sua cartella `job_N/` su EOS, così i 30
job non si sovrascrivono a vicenda l'output e le immagini.

**`condorSub.sub`** — il file di submit. `queue name matching files
(jobs/do_*.sh)` fa partire un job per ogni script generato. Gli output vanno su
EOS e non su AFS, perché i nodi di condor hanno accesso in scrittura ad AFS poco
affidabile.

**`merge.py`** — unisce i 30 output con `hadd` e **ricalcola** il
`TGraphErrors` degli RMS. Questo passaggio è necessario: gli istogrammi si
sommano correttamente, ma `hadd` su un `TGraph` si limita a impilare i 30
grafici uno sull'altro invece di combinarli. Rigenera anche tutti i plot con la
statistica completa e stampa il numero di muoni per bin.

**`fix_xcenter.py`** — sposta i punti del grafico RMS vs $p_T$ dal centro
geometrico del bin al $\langle p_T \rangle$ reale dei muoni che ci cadono
dentro. Serve soprattutto per l'ultimo bin (120-500 GeV): lo spettro cade
ripidamente, quindi quasi tutti i muoni stanno vicino a 120-150 GeV e mettere il
punto a 310 GeV è fuorviante. Gira in interattivo su un file solo, perché per
una media basta pochissima statistica, e aggiorna `config.py` (con backup in
`config.py.bak`). Dopo basta rilanciare `merge.py`, non serve rifare i job.

## I plot in `images/`

Ogni tipo di plot esiste in due versioni: quella inclusiva (tutti i muoni) e
quella con suffisso **`_prompt`**, identica ma riempita solo con i muoni
truth `IFFType == 4`. Di seguito il dettaglio delle tre versioni prompt
citate spesso in tesi (le equivalenti senza suffisso sono le stesse cose
sulla popolazione inclusiva):

- **`h_res_all_prompt`** — istogramma della risoluzione in curvatura
  (100 bin tra -0.2 e 0.2) riempito con **tutti** i muoni prompt insieme,
  senza distinzione di bin di $p_T$. In legenda: numero di entries, media e
  RMS della distribuzione. È il plot "d'insieme", da confrontare con
  `h_res_all` per vedere quanto la componente non-prompt (muoni da
  decadimenti di adroni pesanti, in volo, ecc.) allarga la coda della
  risoluzione totale.

- **`plot_bins_overlay_prompt`** — i 7 istogrammi di risoluzione per bin di
  $p_T^{truth}$ (0-20, 20-30, ..., 120-500 GeV), sui soli muoni prompt,
  sovrapposti sullo stesso canvas dopo aver normalizzato ciascuno a area 1
  (`h.Scale(1/h.Integral())`). La normalizzazione è quello che permette di
  confrontare la **forma** delle distribuzioni indipendentemente dal numero
  di muoni in ciascun bin (che cala rapidamente ad alto $p_T$): si vede a
  colpo d'occhio come la risoluzione peggiori (distribuzione più larga)
  andando verso $p_T$ più alti. Colori dalla palette ATLAS-like di
  `style.py`, un colore per bin, legenda con il range di ciascuno.

- **`rms_vs_pt_prompt`** — il plot finale della risoluzione: un
  `TGraphErrors` con l'RMS di ciascun istogramma di bin (asse y) in funzione
  del $p_T^{truth}$ (asse x), solo muoni prompt. Le barre **orizzontali**
  non sono un errore ma la larghezza del bin in $p_T$ (dopo `fix_xcenter.py`
  il punto è posizionato al $\langle p_T\rangle$ reale dei muoni nel bin, non
  al centro geometrico — per questo l'ultimo bin, 120-500 GeV, ha il punto
  spostato verso i 120-150 GeV); le barre **verticali** sono l'errore
  statistico sull'RMS (`GetRMSError()`), piccolissime con la statistica
  piena. È il grafico che riassume "come peggiora la risoluzione in $p_T$
  al crescere del $p_T$" ed è quello che va confrontato con l'equivalente
  inclusivo (`rms_vs_pt`) per isolare l'effetto della sola componente
  prompt.

Oltre a questi, `images/` contiene anche `plot_range_<min>_<max>[_prompt]` —
un istogramma per singolo bin di $p_T$ (non normalizzato, con Entries e RMS
in legenda), cioè i singoli pezzi che compongono l'overlay sopra.

**`h_res_prompt_vs_incl`** — overlay diretto tra `h_res_all` (inclusivo) e
`h_res_all_prompt`, entrambi normalizzati a densità, con RMS e frazione di
muoni non-prompt in legenda. Da `draw_prompt_vs_inclusive` in `plotting.py`,
regenerato automaticamente da `merge.py`. È il plot pensato per la tesi: le
due distribuzioni sono visivamente quasi indistinguibili — la
giustificazione quantitativa del perché è nella sezione seguente.

## Inclusivo vs prompt: giustificazione

Confronto tra `h_res_all` e `h_res_all_prompt` sulla statistica piena (da
`output_risoluzione.root`, 30 file, PerfectAlignment):

| | Entries | Mean | RMS |
|---|---:|---:|---:|
| inclusivo | 160'051'113 | 0.00278 | 0.02879 |
| prompt | 158'848'216 | 0.00293 | 0.02846 |

Solo lo **0.75%** dei muoni ricostruiti e matchati al truth non è prompt
(`IFFType != 4`), e infatti sull'istogramma "tutto insieme" la differenza di
RMS è piccola (~1% relativo, appena visibile nell'overlay
`h_res_prompt_vs_incl`). Guardando però come si distribuisce quello 0.75%
per bin di $p_T^{truth}$, la storia è diversa:

| bin $p_T$ | non-prompt | RMS inclusivo | RMS prompt |
|---|---:|---:|---:|
| 0-20 GeV | **5.30%** | 0.02975 | 0.02728 |
| 20-30 GeV | 0.06% | 0.02706 | 0.02706 |
| 30-40 GeV | 0.01% | 0.02800 | 0.02800 |
| 40-50 GeV | 0.00% | 0.02894 | 0.02894 |
| 50-80 GeV | 0.01% | 0.03055 | 0.03054 |
| 80-120 GeV | 0.01% | 0.03478 | 0.03478 |
| 120-500 GeV | 0.00% | 0.04204 | 0.04204 |

La contaminazione non-prompt è concentrata quasi interamente nel primo bin
(0-20 GeV, 5.3%); sopra i 20 GeV è sotto lo 0.1% e le due RMS coincidono alla
quarta cifra decimale. È coerente con la cinematica: i muoni prompt da
Z→μμ hanno uno spettro piccato attorno a $m_Z/2 \approx 45$ GeV, mentre i
muoni non-prompt (decadimento in volo di $\pi/K$, decadimento di adroni
pesanti, punch-through calorimetrico) hanno uno spettro molto più soffice
che cade ripidamente sotto i 20-30 GeV — è lì che la loro frazione relativa
esplode.

Il punto forte per la tesi è nel bin 0-20 GeV isolato: la RMS **prompt**
lì (0.02728) è praticamente identica a quella del bin 20-30 GeV (0.02706) —
cioè la risoluzione vera (solo muoni di segnale) è piatta anche a basso
$p_T$. È la RMS **inclusiva** dello stesso bin (0.02975, +9% relativo) a
essere anomala. Questo dimostra che il peggioramento apparente a basso
$p_T$ nel plot puramente inclusivo **non è un effetto di risoluzione del
rivelatore**, ma un artefatto della contaminazione di muoni non-prompt che
si concentra lì (e che spesso hanno un match truth-reco meno pulito, es. un
muone da decadimento in volo la cui traccia ricostruita segue il
pione/kaone genitore solo fino al punto di decadimento). **È la
giustificazione per cui serve lo split prompt/inclusivo**: isola la
risoluzione genuina del rivelatore dalla composizione dell'evento.

### E la crescita della RMS con $p_T$ (in entrambe le curve)?

A differenza della contaminazione non-prompt, la crescita da ~0.027
(20-30 GeV) a ~0.042 (120-500 GeV) è **identica** su inclusivo e prompt —
quindi è un effetto fisico genuino del rivelatore, non di composizione del
campione. Segue la parametrizzazione standard della risoluzione in $p_T$
dello spettrometro a muoni:

$$\frac{\sigma(p_T)}{p_T} = a \oplus b \cdot p_T$$

- termine $a$ (**multiple scattering**): domina a basso/medio $p_T$, circa
  costante — per questo i bin 20-30/30-40/40-50/50-80 GeV sono quasi piatti
  (0.027-0.031);
- termine $b \cdot p_T$ (**risoluzione spaziale intrinseca delle camere**,
  cioè misura della sagitta): a $p_T$ alto la traccia è quasi rettilinea, la
  sagitta da misurare è piccola rispetto alla risoluzione di posizione delle
  camere, e questo termine cresce linearmente con $p_T$ — per questo 80-120
  e 120-500 GeV salgono nettamente (0.035, 0.042).

Motiva anche perché si studia la risoluzione in **curvatura** ($1/p_T$)
invece che in $p_T$ diretto: è la quantità effettivamente fittata nello
spettrometro (proporzionale a $q/p_T$), e il suo residuo resta gaussiano su
tutto il range, mentre $\Delta p_T / p_T$ svilupperebbe code asimmetriche ad
alto $p_T$ per via della non linearità di $1/x$.

## Sottocartella `WP`

`WP/` riusa questo stesso campione Z→μμ per rispondere a una domanda diversa:
la risoluzione in curvatura dipende dal working point di qualità del muone
(Loose/Medium/Tight)? Stessa pipeline (config/chain_builder/histograms/
event_loop/plotting/main/gen_jobs/condor), ma solo due tipi di plot invece
di quattro: la risoluzione inclusiva sovrapposta per i tre WP, e
l'efficienza del WP (in p_T, eta, phi) rispetto ai muoni ricostruiti e
matchati al truth. Dettagli, risultati e un bug non ovvio incontrato
(`vector<char>` in PyROOT che rende `bool('\x00')` vero) in `WP/README.md`.

Le immagini prodotte, in `WP/images/`:

- **`h_res_wp_overlay`** — le tre distribuzioni di risoluzione in curvatura
  (Loose/Medium/Tight), ciascuna normalizzata a densità (stessa area, come
  in `plot_bins_overlay`) e sovrapposte sullo stesso canvas, con l'RMS di
  ciascun WP in legenda. Risultato: le tre curve sono praticamente
  indistinguibili (RMS 0.0282/0.0282/0.0259) — la scelta del WP non incide
  sulla risoluzione in $p_T$, solo sull'efficienza.

- **`efficiency_vs_pt`** — efficienza dei tre WP (Loose/Medium/Tight) in
  funzione di $p_T^{truth}$, calcolata con `TEfficiency` (errori
  Clopper-Pearson), binning uniforme 50 bin × 10 GeV in [0, 500] GeV. Il
  denominatore è il muone già ricostruito e matchato al truth (stesso
  identico denominatore della risoluzione), **non** tutti i muoni truth
  generati — vedi `WP/README.md` per la distinzione. Cresce leggermente con
  $p_T$ per Tight, plateau già raggiunto per Loose/Medium.

- **`efficiency_vs_eta`** — idem in funzione di $\eta^{truth}$, 27 bin in
  [-2.7, 2.7]. Mostra un calo netto dell'efficienza a $\eta \approx 0$ per
  Medium (~0.71) e soprattutto Tight (~0.60): è il buco di accettanza dovuto
  ai servizi nella regione centrale del barrel, atteso in ATLAS. Loose lo
  sente molto meno perché include anche muoni segment-tagged e
  calo-tagged, che non richiedono piena copertura dello spettrometro.

- **`efficiency_vs_phi`** — idem in funzione di $\phi^{truth}$, 32 bin in
  [-π, π]. Piatto come atteso: nessun buco settoriale evidente per nessuno
  dei tre WP.

## Note

Nel grafico RMS vs $p_T$ le barre orizzontali sono la **larghezza dei bin**, non
un errore: quella dell'ultimo punto è larga perché il bin va da 120 a 500 GeV.
Gli errori statistici sono quelli verticali, e con la statistica piena sono
molto piccoli.

## Da controllare

Il conteggio dà circa 12 muoni per evento, mentre in uno Z→μμ me ne aspetterei
~2. Va capito se l'ntupla salva molti candidati muone o se più muoni ricostruiti
puntano allo stesso indice truth: nel secondo caso ci sono duplicati e la
statistica effettiva è più bassa di quella nominale.

Prossimo passo: ripetere l'analisi sul campione Z′.
