#!/usr/bin/env bash

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

echo "DEPRECATION: Use ${SCRIPT_HOME}/create_fuseki_index.sh directly!" >&2
"${SCRIPT_HOME}/create_fuseki_index.sh" "int"
