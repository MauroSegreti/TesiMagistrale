#!/bin/bash
ANADIR=/afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_analysis/WP
OUTDIR=/eos/user/m/masegret/wp_out
DATASET=/eos/user/m/masegret/PerfectAlignment/user.lucam.mc23_13p6TeV.601190.PhPy8EG_AZNLO_Zmumu.MCP_TESTNTUP.mc23e_ANALYSIS.root

ls -d $DATASET/*.root > files.txt
N=$(wc -l < files.txt)
echo "[INFO] $N file trovati -> $N job"

mkdir -p jobs logs $OUTDIR
rm -f jobs/do_*.sh

i=0
while read -r f; do
    cat > jobs/do_$i.sh <<EOF
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
    chmod +x jobs/do_$i.sh
    i=$((i+1))
done < files.txt

echo "[INFO] generati $i script in jobs/"
