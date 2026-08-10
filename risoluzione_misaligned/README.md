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
