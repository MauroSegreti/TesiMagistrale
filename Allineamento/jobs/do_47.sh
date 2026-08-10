#!/bin/bash
unset DISPLAY
echo "Running on host $(hostname)"
echo "Lista: /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_quantili/jobs/list_0047.txt"
cat /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_quantili/jobs/list_0047.txt

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

# proxy VOMS trasferito da condor (x509userproxy nel .sub): serve per
# leggere i file via XRootD
echo "X509_USER_PROXY = $X509_USER_PROXY"
voms-proxy-info -exists -valid 0:10 || echo "[WARNING] proxy assente o scaduto"

export PYTHONPATH=/afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_quantili:$PYTHONPATH

WORK=/eos/user/m/masegret/risoluzione_quantili_out/job_47
mkdir -p $WORK
cd $WORK

python3 /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_quantili/fill.py /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_quantili/jobs/list_0047.txt
echo "Exit code: $?"
