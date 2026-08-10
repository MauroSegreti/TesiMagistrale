# Risoluzione in $p_T$ dei muoni — campioni MS-misaligned

Stessa identica misura di [`risoluzione_quantili`](../risoluzione_quantili/) —
stesso binning, stesso stimatore ($\sigma_{68}$), stesso fit a 3 termini,
stesso codice — ma sui campioni con **geometria disallineata** (tag
`mc23e_MSmisalign`) invece di `PerfectAlignment`. Per i dettagli su metodo,
formula, e come si legge il fit, vedi il README di `risoluzione_quantili`:
qui non li ripeto.

Questa cartella conteneva una versione precedente (fit gaussiano puro,
binning tarato a mano sui picchi jacobiani): sostituita perché va confrontata
punto per punto con `risoluzione_quantili`, non con una metodologia diversa —
altrimenti la differenza fra i due $r_2$ mescola l'effetto
dell'allineamento con quello del metodo (vedi la sistematica "d_metodo" nel
README di `risoluzione_quantili`, non trascurabile: 15-30% relativo).

## Campioni (tag `mc23e_MSmisalign`, prodotti da `user.lucam`)

| DSID | campione |
|---|---|
| 601190 | Z → μμ (Powheg+Pythia8 AZNLO) |
| 801862 | Z′ ZeroWidth 500 GeV |
| 801863 | Z′ ZeroWidth 1000 GeV |
| 801864 | Z′ ZeroWidth 3000 GeV |
| 801865 | Z′ ZeroWidth 5000 GeV |
| 801866 | Z′ ZeroWidth 8000 GeV |

Stessi sei DSID di `risoluzione_quantili`, tag diverso.

## Preparare le liste

Stesso schema di `PerfectAlignment`: una lista `.root.txt` per DSID, con URL
`root://`, in `/afs/cern.ch/user/m/masegret/MisAligned_MC`. Nessun download:
`gen_jobs.sh` legge questi file via XRootD.

```bash
setupATLAS
lsetup rucio
voms-proxy-init -voms atlas

mkdir -p /afs/cern.ch/user/m/masegret/MisAligned_MC
cd /afs/cern.ch/user/m/masegret/MisAligned_MC

rucio list-dids --short 'user.lucam:user.lucam.mc23_13p6TeV.*.MCP_TESTNTUP.mc23e_MSmisalign_ANALYSIS.root' \
  | sed 's/^user.lucam://' | grep . > /tmp/dids.txt
while read NAME; do
  rucio list-file-replicas --protocols root --pfns "user.lucam:${NAME}" \
    | grep -o 'root://[^ ]*' | sort -u > "${NAME}.root.txt"
  echo "$NAME -> $(wc -l < "${NAME}.root.txt") file"
done < /tmp/dids.txt
```

Controlla che vengano fuori sei file `.txt`, uno per DSID della tabella sopra.

## Come giro

```bash
setupATLAS
voms-proxy-init -voms atlas --valid 24:00
cp /tmp/x509up_u$(id -u) $HOME/x509up
chmod 600 $HOME/x509up
export X509_USER_PROXY=$HOME/x509up

./gen_jobs.sh
condor_submit condorSub.sub
```

Analisi:

```bash
python3 analyze.py /eos/user/m/masegret/risoluzione_misaligned_out
python3 inspect_bins.py merged_res.root
```

## Prima del primo giro vero

`EXPECTED_R2` in `config.py` è già alzato rispetto al nominale (il
disallineamento peggiora $r_2$, è il termine sensibile all'allineamento) ma è
una stima: se `print_window_summary()` o troppi bin scartati per outflow lo
smentiscono, alzalo ancora — dimensiona solo la finestra, non entra nel
risultato.

`PT_FIT_MAX` e `MIN_REL_ERR` sono ereditati dal nominale come punto di
partenza, ma sono stati calibrati là sui dati di `PerfectAlignment`: vanno
ricontrollati qui allo stesso modo (vedi il README di `risoluzione_quantili`
per il procedimento — in breve, il floor giusto è quello che porta
chi2/ndf ≈ 1, non un numero scelto a caso).

## Risultati

Primo giro: 31 job sottomessi (26 Zmumu + 5 Z′, tutti `user.lucam`), 30
completati — `job_24` (un file Zmumu su MPCDF) è andato in errore per un
redirect XRootD, non un problema della misura. Nessun bin scartato per
outflow con l'`EXPECTED_R2` alzato.

### Fit (q68, fino a 800 GeV, floor 10% ereditato dal nominale)

| $\|\eta\|$ | $r_0$ [GeV] | $r_1$ | $r_2$ [$10^{-3}$ GeV$^{-1}$] | $\chi^2$/ndf |
|---|---|---|---|---|
| 0.0 - 0.1 | 0.000 ± 45.2 | 0.0182 ± 0.0014 | 0.311 ± 0.015 | 0.16 |
| 0.1 - 1.05 | 0.000 ± 30.9 | 0.0209 ± 0.0011 | 0.192 ± 0.011 | 0.67 |
| 1.05 - 1.3 | 0.001 ± 38.3 | 0.0229 ± 0.0014 | 0.270 ± 0.014 | 0.29 |
| 1.3 - 1.7 | 0.000 ± 45.3 | 0.0290 ± 0.0016 | 0.283 ± 0.016 | 0.20 |
| 1.7 - 2.5 | 0.000 ± 49.4 | 0.0269 ± 0.0015 | 0.278 ± 0.015 | 0.05 |
| 2.5 - 2.8 | 0.404 ± 0.347 | 0.0309 ± 0.0044 | 0.430 ± 0.024 | 0.06 |

Chi2/ndf tutti $\lesssim 1$, anche troppo bassi: il floor del 10% è stato
calibrato sulla dispersione punto-punto del *nominale*, che ha statistica
molto più alta (73 file contro 31). Qui probabilmente è più largo del
necessario — da ricalibrare (stesso procedimento del nominale) se serve un
$\chi^2$/ndf realistico invece che solo "il fit converge bene".

### Confronto diretto con il nominale — il risultato della tesi

Stesso identico metodo e binning, quindi $r_2$ è confrontabile punto per
punto: la sola differenza è la geometria.

| $\|\eta\|$ | $r_2$ nominale | $r_2$ misaligned | rapporto |
|---|---|---|---|
| 0.0 - 0.1 | 0.224 ± 0.065 | 0.311 ± 0.051 | 1.4× |
| 0.1 - 1.05 | 0.126 ± 0.028 | 0.192 ± 0.027 | 1.5× |
| 1.05 - 1.3 | 0.124 ± 0.030 | 0.270 ± 0.030 | 2.2× |
| 1.3 - 1.7 | 0.161 ± 0.053 | 0.283 ± 0.028 | 1.8× |
| 1.7 - 2.5 | 0.089 ± 0.026 | 0.278 ± 0.030 | 3.1× |
| 2.5 - 2.8 | 0.104 ± 0.021 | 0.430 ± 0.062 | 4.1× |

($r_2$ in $10^{-3}$ GeV$^{-1}$, errori stat+syst in quadratura; vedi
`images/plot_confronto_allineamento.png` per la curva completa e
`compare_alignment.py` per come è fatto)

**La degradazione da disallineamento cresce con $|\eta|$**: da ~1.4× nel
barrel centrale a ~4× nel forward (2.5-2.8). È fisicamente sensato: oltre
$|\eta| = 2.5$ le tracce sono standalone nel muon spectrometer (niente inner
detector, vedi i tre termini nel README di `risoluzione_quantili`), quindi
meno misure ridondanti per compensare l'errore di posizione delle camere
disallineate. Il barrel centrale, dove $r_2$ è già il più piccolo dei due
casi, è anche il più protetto dal disallineamento in termini relativi.
