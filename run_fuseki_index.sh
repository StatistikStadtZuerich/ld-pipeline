#!/bin/bash

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

ENV_NAME="${1:-local}"

LOG_DIR="${LOG_DIR:-/home/lod_pipeline/logs}"
DATE_SUFFIX=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/fuseki_index_${ENV_NAME}_${DATE_SUFFIX}.log"

"${SCRIPT_HOME}/create_fuseki_index.sh" "$ENV_NAME" >> "$LOG_FILE" 2>&1
