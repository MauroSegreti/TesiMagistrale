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

## Sottocartella `WP`

`WP/` riusa questo stesso campione Z→μμ per rispondere a una domanda diversa:
la risoluzione in curvatura dipende dal working point di qualità del muone
(Loose/Medium/Tight)? Stessa pipeline (config/chain_builder/histograms/
event_loop/plotting/main/gen_jobs/condor), ma solo due tipi di plot invece
di quattro: la risoluzione inclusiva sovrapposta per i tre WP, e
l'efficienza del WP (in p_T, eta, phi) rispetto ai muoni ricostruiti e
matchati al truth. Dettagli, risultati e un bug non ovvio incontrato
(`vector<char>` in PyROOT che rende `bool('\x00')` vero) in `WP/README.md`.

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
