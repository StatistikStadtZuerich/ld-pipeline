#!/bin/bash

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

echo "DEPRECATION: Use ${SCRIPT_HOME}/run_pipeline.sh directly!" >&2
"${SCRIPT_HOME}/run_pipeline.sh" "int"
