#!/bin/bash


ALGO="MyFirstAlgo"
BASE="$PWD/algo/python/test_deployment"
CONFIG="$BASE/config/config.json"
RESULTS="$BASE/results"

echo "Executing ${ALGO} ... "

# need to run as super user otherwise lean complains it cannot write files ...
sudo mono ../Launcher/bin/Debug/QuantConnect.Lean.Launcher.exe --config $CONFIG  \
#  --results-destination-folder "$RESULTS" \
  |& tee runlogs/"$ALGO.out"

echo "Done Executing ${ALGO}"
