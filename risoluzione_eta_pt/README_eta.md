# Risoluzione in $p_T$ vs $|\eta^{truth}|$ — Z→μμ

Estensione dell'analisi sulla risoluzione in $p_T$: qui invece di un solo
andamento in $p_T$ studio come la risoluzione dipende **anche** da
$|\eta^{truth}|$, con una selezione combinata sui due.

La variabile è sempre la risoluzione in curvatura,

$$\frac{1/p_T^{reco} - 1/p_T^{truth}}{1/p_T^{truth}} = \frac{p_T^{truth}}{p_T^{reco}} - 1$$

ma la riempio in una griglia **6 × 6**: 6 bin di $p_T$ (20-30, 30-40, 40-50,
50-80, 80-120, 120-500 GeV) per 6 bin di $|\eta|$. Da ogni istogramma prendo
l'RMS, e il risultato è un grafico con una curva per bin di $p_T$, in funzione
di $|\eta|$.

Qui uso **solo i muoni truth prompt** (`IFFType == 4`), a differenza
dell'analisi precedente che aveva anche la versione inclusiva.

## I bin in $\eta$

Non sono uniformi: seguono la geometria dello spettrometro.

| bin | regione |
|---|---|
| 0.0 - 0.1 | crack centrale, muoni calo/segment-tagged, risoluzione peggiore |
| 0.1 - 1.01 | barrel, poco multiple scattering, buon $B \times L$ |
| 1.01 - 1.3 | transizione barrel/endcap |
| 1.3 - 1.7 | inversioni di campo, risoluzione peggiore |
| 1.7 - 2.5 | endcap, shielding davanti alla prima camera |
| 2.5 - 2.8 | endcap senza inner detector, solo tracce stand-alone |

L'andamento che ottengo riproduce questa struttura: minimo nel barrel, gobba
nella regione di transizione, e risalita netta oltre $|\eta| = 2.5$.

## Come giro

Stesso schema dell'analisi in $p_T$: 30 job HTCondor in parallelo, uno per file
di input, invece di un unico processo interattivo che verrebbe ucciso dalla
sessione. Circa 4 minuti a job.

Setup dell'ambiente, per accedere ai dataset con rucio:

```bash
setupATLAS
voms-proxy-init -voms atlas
lsetup rucio
```

Il setup di ROOT sta dentro gli script generati da `gen_jobs_eta.sh`, così ogni
job se lo fa da solo sulla macchina su cui gira.

Generazione dei job e submit:

```bash
cd ~/TesiMagistrale/risoluzione_eta_pt

grep MAX_EVENTS config.py        # -1 per girare su tutto
./gen_jobs_eta.sh                # crea jobs/do_0.sh ... do_29.sh
condor_submit condorSub.sub
condor_q
```

Prima del submit completo provo sempre **un job solo**:

```bash
sed 's|jobs/do_\*.sh|jobs/do_0.sh|' condorSub.sub > condorTest.sub
condor_submit condorTest.sub
cat logs/do_0.sh.err
ls -la /eos/user/m/masegret/risoluzione_eta_out/job_0/
```

Quando `condor_q` è vuoto, controllo che ci siano tutti gli output e unisco:

```bash
ls -d /eos/user/m/masegret/risoluzione_eta_out/job_*/output_eta.root | wc -l   # 30
grep -l Traceback logs/*.err                                                   # nulla
python3 merge_eta.py /eos/user/m/masegret/risoluzione_eta_out
```

Se qualche job è morto, per capire quali e rilanciarli:

```bash
for i in $(seq 0 29); do
  [ -f /eos/user/m/masegret/risoluzione_eta_out/job_$i/output_eta.root ] || echo "manca job_$i"
done

mkdir -p retry && cp jobs/do_14.sh jobs/do_25.sh retry/
sed 's|jobs/do_\*.sh|retry/do_*.sh|' condorSub.sub > condorRetry.sub
condor_submit condorRetry.sub
```

## I file

**`config.py`** — bin di $p_T$ e di $|\eta|$, nome del TTree, `MAX_EVENTS`
(a `-1` per girare su tutto, un valore positivo per i test rapidi) e il tipo
IFF dei muoni prompt.

**`chain_builder.py`** — costruisce la `TChain` da un singolo `.root`, da una
lista Rucio `.root.txt` con URL XRootD, o da una cartella (in cui cerca
ricorsivamente entrambi).

**`histograms.py`** — crea la griglia $p_T \times \eta$ di istogrammi (100 bin
tra -0.2 e 0.2), organizzata come dict `{bin_pT: [h_eta_0, h_eta_1, ...]}`.

**`event_loop.py`** — il loop sugli eventi. Segue `muon_truthmuon_index` per
risalire al muone truth, tiene solo i prompt, calcola la risoluzione e la mette
nell'istogramma corrispondente alla coppia (bin $p_T$, bin $|\eta|$).

**`plotting.py`** — per ogni bin di $p_T$ costruisce il `TGraphErrors` di RMS vs
$|\eta|$ e li disegna tutti sovrapposti. La legenda sta nel margine destro,
fuori dall'area dati, così non copre mai le curve.

**`report.py`** — genera la tabella PDF con entries, RMS ed errore per tutte le
36 combinazioni. È disegnata interamente con ROOT (TBox/TLine/TLatex), quindi
non serve nessuna libreria PDF esterna oltre all'ambiente che uso già.

**`style.py`** — stile ATLAS-like e palette dei colori.

**`main.py`** — costruisce la chain, gira il loop, salva la griglia in
`output_eta.root` e produce plot e tabella. È quello che lancia ogni job di
condor, su un file alla volta. Il salvataggio del `.root` è indispensabile:
senza, ogni job produrrebbe solo i suoi plot parziali e non ci sarebbe niente
da unire.

**`gen_jobs_eta.sh`** — genera uno script `jobs/do_N.sh` per ogni file di input.
Ricava da solo il path della cartella di analisi, quindi non c'è niente da
modificare a mano. Ogni job lavora in `job_N/` su EOS, così i 30 non si
sovrascrivono a vicenda.

**`condorSub.sub`** — il file di submit: un job per ogni script generato.
Gli output vanno su EOS e non su AFS, perché i nodi condor hanno accesso in
scrittura ad AFS poco affidabile.

**`merge_eta.py`** — unisce i 30 output con `hadd` e **ricostruisce** i
`TGraphErrors` dagli istogrammi sommati: `hadd` sa sommare gli istogrammi ma sui
`TGraph` si limiterebbe a impilarli. Rigenera plot e tabella con la statistica
completa e segnala i bin con meno di 100 muoni.

## Note

Nella tabella l'errore sull'RMS appariva come `0.0000`: non è un problema del
codice, è arrotondamento. L'errore vale circa $\text{RMS}/\sqrt{2N}$ e con
milioni di muoni per bin sta sotto $10^{-5}$. L'ho portato a 6 decimali in
`report.py`. Con questa statistica l'incertezza statistica è comunque
trascurabile: quello che conta sono le sistematiche.

## Da controllare

Nel primo giro completo hanno prodotto output **28 job su 30** (mancavano
`job_14` e `job_25`), quindi quel merge usa il 93% della statistica. I 30 file
di input sono tutti presenti in locale, quindi non è un problema di download
mancato: va guardato `logs/do_14.sh.err` per capire la causa e rilanciare i due
job.

Resta anche da chiarire il totale di entries: la somma dai log dà 88M, mentre
mi aspettavo un dataset più grande. Da verificare file per file prima di usare
questi numeri in tesi.

Prossimo passo: ripetere l'analisi sul campione Z′.
