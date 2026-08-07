# Risoluzione in $p_T$ dei muoni — Z + Z′, allineamento perfetto

Misuro la risoluzione in $p_T$ dei muoni su tutto lo spettro, da 20 GeV a 3 TeV,
combinando la Z standard e i Z′ a varie masse, su MC con geometria **ideale**
(`PerfectAlignment`). Il risultato è il riferimento nominale contro cui
confronterò poi i campioni disallineati.

## Cosa misuro

Per ogni muone ricostruito risalgo al muone truth associato e calcolo la
risoluzione in curvatura:

$$\frac{1/p_T^{reco} - 1/p_T^{truth}}{1/p_T^{truth}} = \frac{p_T^{truth}}{p_T^{reco}} - 1$$

È la variabile giusta perché il tracciamento misura la sagitta, che va come
$1/p_T$: è la curvatura ad avere errore gaussiano, non il $p_T$.

Riempio una griglia 14 × 6 (bin di $p_T$ × bin di $|\eta|$), estraggo da ogni
istogramma la $\sigma$ del core con un fit gaussiano iterativo entro $\pm 2\sigma$,
e fitto l'andamento con

$$\frac{\sigma_{p_T}}{p_T} = \sqrt{\frac{r_0^2}{p_T^2} + r_1^2 + (r_2 \, p_T)^2}$$

Uso solo muoni truth prompt (`IFFType == 4`).

### I tre termini

Ciascuno domina in una regione diversa dello spettro:

**$r_0/p_T$** — fluttuazioni della perdita di energia nel materiale. La perdita è
circa costante in valore assoluto, quindi il suo peso relativo va come $1/p_T$ e
conta solo a basso $p_T$.

**$r_1$** — multiple scattering. Devia il muone in modo che scala con $p_T$ come
la misura stessa, quindi dà un contributo relativo costante: è il plateau
centrale.

**$r_2 \, p_T$** — risoluzione intrinseca del rivelatore. La sagitta va come
$1/p_T$: più il muone è rigido, più la traccia è dritta e più piccola è la
sagitta da misurare. Con un errore di posizione fisso, l'errore relativo cresce
linearmente con $p_T$, e domina in cima.

$r_2$ è il parametro che interessa di più, perché è quello sensibile
all'allineamento: uno spostamento delle camere rispetto a dove il software crede
che siano falsa la sagitta, e ad alto $p_T$ la sagitta è così piccola che bastano
poche decine di micron.

## Perché servono sia la Z sia i Z′

Non sono due campioni da confrontare fra loro: sono entrambi MC, entrambi passati
per la stessa simulazione dello stesso rivelatore con la stessa geometria. Sono
pezzi della **stessa** misura.

In una Z→μμ i muoni hanno $p_T \approx m_Z/2 \approx 45$ GeV e la statistica muore
prima dei 200 GeV. Ogni Z′ produce muoni piccati a $\approx m/2$, quindi popola una
regione diversa: 500 GeV → 250 GeV, 1000 → 500, 3000 → 1500. Messi insieme
coprono tutto lo spettro.

Conseguenza importante: lo spettro combinato **non è una curva liscia**, ha gobbe
alle masse dimezzate e avvallamenti in mezzo. Va tenuto presente leggendo la
statistica per bin.

Il confronto che misura l'allineamento è un altro: stessi identici sample,
geometria diversa (`MisAligned_MC/`).

## Struttura: due fasi

`main.py` è diviso in due script, e la separazione è obbligata.

**`fill.py`** gira nei job condor, uno per file di input: legge, riempie la
griglia $\eta \times p_T$ e salva `output_res.root`. Nessun fit.

**`analyze.py`** gira dopo, una volta sola: `hadd` di tutti gli output, poi fit,
plot e tabelle.

Il fit non si può fare dentro i job perché la funzione si aggiusta su tutti i
punti in $p_T$ insieme, e quei punti vengono da campioni diversi. Un job che vede
un solo file non ha la curva da fittare.

Dettaglio tecnico: `pt_sums` e `pt_counts`, che servono a mettere ogni punto al
$p_T$ medio effettivo del bin invece che al centro geometrico, sono salvati come
due `TH2D` (`h_pt_sum`, `h_pt_count`) proprio perché `hadd` li sommi insieme agli
istogrammi. Come dizionari Python sarebbero andati persi nel merge.

## Come giro

I Z′ non sono scaricati: le liste Rucio `.root.txt` contengono URL `root://` e i
job leggono i file **via XRootD** senza copia locale. Serve quindi un proxy VOMS
trasferito ai nodi.

```bash
setupATLAS
voms-proxy-init -voms atlas --valid 24:00
cp /tmp/x509up_u$(id -u) $HOME/x509up
chmod 600 $HOME/x509up
export X509_USER_PROXY=$HOME/x509up
```

Il proxy va messo su AFS e non in `/tmp`: `/tmp` è locale alla macchina e lo
schedd (`bigbird15`) non lo vede, quindi i job finiscono in `HOLD` con
`Transfer input files failure`.

```bash
./gen_jobs.sh                 # 30 file Z locali + 5 liste Z' = 35 job
condor_submit condorSub.sub
condor_q
```

Prova sempre prima un job singolo, e scegline uno **Z′** (i primi 30 sono la Z),
perché è quello che testa la lettura remota:

```bash
sed 's|jobs/do_\*.sh|jobs/do_30.sh|' condorSub.sub > condorTest.sub
condor_submit condorTest.sub
cat logs/do_30.sh.err
```

Poi l'analisi:

```bash
ls -d /eos/user/m/masegret/risoluzione_combinata_out/job_*/output_res.root | wc -l
python3 analyze.py /eos/user/m/masegret/risoluzione_combinata_out
python3 check_sigma.py merged_res.root 1
```

## I file

**`config.py`** — bin di $p_T$ e $|\eta|$, parametri delle finestre degli
istogrammi, soglie, path di output.

**`chain_builder.py`** — costruisce la `TChain` da un file `.root`, da una lista
Rucio `.txt` di URL, o da una cartella.

**`histograms.py`** — griglia $\eta \times p_T$ di istogrammi, con finestra
dimensionata sul $p_T$ del bin e allargata per bin di $\eta$
(`ETA_WINDOW_SCALE`), più i due `TH2D` accumulatori del $p_T$ medio.

**`event_loop.py`** — il loop: truth matching, selezione prompt, calcolo della
risoluzione, riempimento della cella giusta.

**`resolution.py`** — estrae la $\sigma$ del core con fit gaussiano iterativo
entro $\pm 2\sigma$, con controlli su entries minime e frazione in
over/underflow.

**`fitting.py`** — costruisce i `TGraphErrors` di $\sigma$ vs $p_T$ per bin di
$\eta$ e li fitta con la formula a tre termini, in due versioni ($r_0$ libero e
$r_0 = 0$), partendo da sei seed diversi e tenendo il migliore fra quelli
convergiuti.

**`plotting.py`** — il plot principale in scala log-log con il pannello dei
residui $(\text{dato}-\text{fit})/\text{fit}$ sotto.

**`report.py`** — tabella PDF con i parametri del fit, disegnata con ROOT.

**`check_sigma.py`** — diagnostica: confronta RMS, fit gaussiano a $\pm 2$,
$\pm 2.5$, $\pm 3\sigma$ e semi-ampiezza dell'intervallo al 68%, e salva la
griglia degli istogrammi con i fit sovrapposti.

**`fill.py` / `analyze.py`** — le due fasi descritte sopra.

**`gen_jobs.sh` / `condorSub.sub`** — generazione dei job e submit.

## Risultati (primo giro completo)

| $\|\eta\|$ | $r_0$ [GeV] | $r_1$ | $r_2$ [$10^{-3}$ GeV$^{-1}$] | $\chi^2$/ndf |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.000 ± 0.029 | 0.0168 | 0.184 | 1332 |
| 0.1 - 1.05 | 0.000 ± 0.002 | 0.0183 | 0.090 | 18370 |
| 1.05 - 1.3 | 0.000 ± 0.037 | 0.0201 | 0.075 | 1276 |
| 1.3 - 1.7 | 0.000 ± 0.015 | 0.0280 | 0.103 | 4906 |
| 1.7 - 2.5 | 0.000 ± 0.022 | 0.0240 | 0.080 | 1911 |
| 2.5 - 2.8 | **0.248 ± 0.003** | 0.0238 | 0.100 | **26** |

$r_2$ peggiore a $|\eta| < 0.1$, il doppio degli altri: è il crack centrale, dove
lo spettrometro ha l'apertura per i servizi del rivelatore interno.

$r_0$ torna esattamente zero nei bin 0-4, al limite inferiore, e i fit con $r_0$
libero e fissato danno $r_1$ e $r_2$ identici: il termine $r_0/p_T$ conta solo a
$p_T$ basso e il punto più basso è a 25 GeV. Nel bin 2.5-2.8 invece $r_0$ è
misurabile e significativo, con il fit libero nettamente migliore (26 contro
166): lì non c'è inner detector, le tracce sono stand-alone e le fluttuazioni di
perdita di energia pesano molto di più.

## Problemi aperti

**Il modello a tre termini non descrive i dati.** Calcolando quale $r_2$
servirebbe per ogni singolo punto (a $r_1$ fissato) nel bin 0.1-1.05:

| $p_T$ [GeV] | 81 | 118 | 239 | 413 | 1015 | 1410 | 2759 |
|---|---|---|---|---|---|---|---|
| $r_2$ efficace [$10^{-4}$] | 1.88 | 1.75 | 1.37 | 1.11 | 0.86 | 0.78 | 0.51 |

Non è costante, scende di un fattore quattro. La $\sigma$ misurata cresce come
$p_T^{0.55}$, non linearmente. I residui arrivano a $\pm 40$-50%.

**$r_2$ dipende dal range del fit.** Rifacendo il fit solo fino a 2 TeV cambia del
22-35% nei bin centrali (0.090 → 0.112, 0.075 → 0.101). Un parametro che si
sposta di un terzo cambiando il range non è una misura solida.

**I $\chi^2$/ndf sono enormi ma non per il motivo che sembra.** Gli errori sulle
$\sigma$ sono minuscoli (decine di milioni di muoni per bin), quindi il $\chi^2$ è
dominato dalla regione a basso $p_T$ e i punti sopra il TeV pesano quasi zero: il
fit li ignora e ci passa sopra. Il paradosso è che $r_2$ descrive proprio l'alto
$p_T$, cioè è determinato dalla regione dove il fit non guarda.

**L'estrazione della $\sigma$, invece, è sana.** Verificato con `check_sigma.py`:
`q68/g2.0` sta fra 1.05 e 1.14, la $\sigma$ cresce del 5-8% passando da $\pm 2$ a
$\pm 3\sigma$, i valori sono monotoni. Le code ci sono ma sono modeste, il core
non collassa.

**Il binning ad alto $p_T$ era troppo grosso.** Le finestre erano dimensionate su
`EXPECTED_R2 = 3e-4` mentre il valore misurato è $\sim 1e-4$: a 2.7 TeV la
finestra era $\pm 4.95$ per una $\sigma$ di 0.14, cioè 3.4 bin per sigma invece di
20. Ritarato a `EXPECTED_R2 = 1.2e-4` e `HIST_N_BINS = 400`, da rigirare.

**Sample ZeroWidth5000 (801865) mancante.** Il job fallisce con
`TNetXNGFile::Open: [FATAL] Redirect limit has been reached`. Produce muoni a
$\approx 2500$ GeV e la sua assenza lascia un buco visibile: nel bin 1750-2500 ho
553 muoni a $|\eta|<0.1$ e 1147 a 1.7-2.5, contro le decine di migliaia dei bin
adiacenti.

## Domande per Luca

1. **Quale range di fit citare?** $r_2$ cambia del 22-35% fra il fit fino a 2 TeV
   e quello fino a 3 TeV. Meglio fissare un range e dichiararlo, o quotare $r_2$
   con una banda che copra la variazione?

2. **La formula a tre termini è ancora la parametrizzazione giusta qui?** La
   $\sigma$ cresce come $p_T^{0.55}$ su due decadi, non linearmente. Ha senso
   fittare solo sopra una certa soglia, dove il termine $r_2$ dovrebbe dominare,
   invece che su tutto lo spettro?

3. **$r_0$ libero o fissato?** Nei bin centrali è indeterminato (torna 0 al
   limite, e i due fit sono identici), nel bin 2.5-2.8 è significativo e fissarlo
   peggiora molto il fit. Uso convenzioni diverse per bin diversi, o la stessa
   ovunque?

4. **Che errore associare a $r_2$?** Quello del fit è puramente statistico e
   assurdamente piccolo. Ha senso costruire una sistematica dalla variazione con
   la finestra di fit gaussiano (5-8% fra $\pm 2$ e $\pm 3\sigma$) e dalla
   variazione con il range in $p_T$?

5. **Quale stimatore della larghezza?** Fit gaussiano sul core a $\pm 2\sigma$
   come adesso, oppure q68 che non assume nessuna forma? Differiscono del 5-14%.

6. **Il ZeroWidth5000 è recuperabile?** Via XRootD non è raggiungibile. Esiste
   un'altra replica, o una copia locale?

7. **`PT_TRUTH_MAX` è a 3000 GeV**, ma il Z′ da 8000 produce muoni a $\approx 4$
   TeV, che vengono tagliati e contribuiscono solo con la coda bassa. Ha senso
   alzarlo, o 3 TeV è il limite giusto per questa analisi?

## Prossimo passo

Ripetere tutto sui campioni in `MisAligned_MC/` e confrontare i $r_2$. Prima però
vanno chiuse le domande sopra: confrontare due numeri non ben definiti in
nessuno dei due campioni non direbbe nulla.
