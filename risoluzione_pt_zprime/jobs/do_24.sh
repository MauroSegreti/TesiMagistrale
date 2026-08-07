#!/bin/bash
unset DISPLAY
echo "Running on host $(hostname)"
echo "Lista: /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_pt_zprime/jobs/list_0024.txt"
cat /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_pt_zprime/jobs/list_0024.txt

export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh
lsetup "root 6.40.02-x86_64-el9-gcc15-opt"

# il proxy VOMS viene trasferito da condor (x509userproxy nel .sub):
# serve per leggere i file remoti dei Z' via XRootD
echo "X509_USER_PROXY = $X509_USER_PROXY"
voms-proxy-info -exists -valid 0:10 || echo "[WARNING] proxy assente o scaduto"

export PYTHONPATH=/afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_pt_zprime:$PYTHONPATH

WORK=/eos/user/m/masegret/risoluzione_combinata_out/job_24
mkdir -p $WORK
cd $WORK

python3 /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_pt_zprime/fill.py /afs/cern.ch/user/m/masegret/TesiMagistrale/risoluzione_pt_zprime/jobs/list_0024.txt
echo "Exit code: $?"
