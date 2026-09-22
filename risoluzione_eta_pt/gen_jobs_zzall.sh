#!/bin/bash
# Genera un job condor per ciascuno dei 68 file Z aligned (files.txt,
# stesso campione di images/) + i 5 file Z' aligned (dati_locali/ su EOS),
# uno per massa (500-8000 GeV). Ogni job gira main_zzall.py (griglia pT
# estesa a 3 TeV) su un solo file. Tutti i file sono locali su EOS,
# nessun proxy VOMS necessario.
#
# Uso:  ./gen_jobs_zzall.sh
# Poi:  condor_submit condorSub_zzall.sub

ANADIR=$(cd "$(dirname "$0")" && pwd)
OUTDIR=/eos/user/m/masegret/risoluzione_zzall_out
DATI_LOCALI=/eos/user/m/masegret/dati_locali

FILELIST="$ANADIR/files_zzall.txt"
cat "$ANADIR/files.txt" > "$FILELIST"
ls -d "$DATI_LOCALI"/user.mmarr.mc23_13p6TeV.80186*/*.root >> "$FILELIST"

N=$(wc -l < "$FILELIST")
echo "[INFO] Analisi in: $ANADIR"
echo "[INFO] Output in:  $OUTDIR"
echo "[INFO] $N file trovati (Z aligned + Z' aligned) -> $N job"

mkdir -p "$ANADIR/jobs_zzall" "$ANADIR/logs_zzall" $OUTDIR
rm -f "$ANADIR"/jobs_zzall/do_*.sh

i=0
while read -r f; do
    cat > "$ANADIR/jobs_zzall/do_$i.sh" <<EOF
#!/bin/bash
unset DISPLAY
echo "Running on host \$(hostname)"
echo "Input file: $f"

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source \$ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

export PYTHONPATH=$ANADIR:\$PYTHONPATH

WORK=$OUTDIR/job_$i
mkdir -p \$WORK
cd \$WORK

python3 $ANADIR/main_zzall.py $f
echo "Exit code: \$?"
EOF
    chmod +x "$ANADIR/jobs_zzall/do_$i.sh"
    i=$((i+1))
done < "$FILELIST"

echo "[INFO] generati $i script in $ANADIR/jobs_zzall/"
