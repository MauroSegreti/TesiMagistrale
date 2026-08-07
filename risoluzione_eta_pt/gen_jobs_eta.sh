#!/bin/bash
# Genera uno script do_N.sh per ogni file di input dell'analisi in eta.
# ANADIR viene ricavato da dove sta questo script, quindi non c'e' niente
# da modificare a mano se sposti la cartella.
#
# Uso:  ./gen_jobs_eta.sh
# Poi:  condor_submit condorSub.sub

ANADIR=$(cd "$(dirname "$0")" && pwd)
OUTDIR=/eos/user/m/masegret/risoluzione_eta_out
DATASET=/eos/user/m/masegret/PerfectAlignment/user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu.MCP_TESTNTUP.mc23e_ANALYSIS.root

echo "[INFO] Analisi in: $ANADIR"
echo "[INFO] Output in:  $OUTDIR"

ls -d $DATASET/*.root > "$ANADIR/files.txt"
N=$(wc -l < "$ANADIR/files.txt")
echo "[INFO] $N file trovati -> $N job"

mkdir -p "$ANADIR/jobs" "$ANADIR/logs" $OUTDIR
rm -f "$ANADIR"/jobs/do_*.sh

i=0
while read -r f; do
    cat > "$ANADIR/jobs/do_$i.sh" <<EOF
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

python3 $ANADIR/main.py $f
echo "Exit code: \$?"
EOF
    chmod +x "$ANADIR/jobs/do_$i.sh"
    i=$((i+1))
done < "$ANADIR/files.txt"

echo "[INFO] generati $i script in $ANADIR/jobs/"
