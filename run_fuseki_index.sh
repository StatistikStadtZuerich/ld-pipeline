#!/bin/bash
set -euo pipefail

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

load_env() {
  # shellcheck source=sample.env disable=SC2015
  [ -r "$1" ] && . "$1" || true
}
findSignal() {
  find "$INPUT_DIR" -maxdepth 1 -type f -name "${1}*.txt" | sort -V | head -1
}

ENV_NAME="${1:-local}"

# load local settings
load_env "${SCRIPT_HOME}/.env"
load_env "${SCRIPT_HOME}/${ENV_NAME}.env"
load_env "./.env"
load_env "./${ENV_NAME}.env"

export JENA_DIR="${JENA_DIR:-/home/lod_pipeline/apache-jena-fuseki-4.9.0/jena}"
export FUSEKI_INDEX_DIR="${FUSEKI_INDEX_DIR:-/home/lod_pipeline/ld-pipeline-2024/fuseki_index/${ENV_NAME}}"
export INPUT_DIR="${INPUT_DIR:-/home/lod_pipeline/ld-pipeline-2024/output/${ENV_NAME}}"
export PIPELINE_DATA_DIR="${PIPELINE_DATA_DIR:-/home/lod_pipeline/hdb_dropzone/prod/test/Pipeline_Data}"
export LOG_DIR="${LOG_DIR:-/home/lod_pipeline/logs}"
DONE_DIR="$INPUT_DIR/done"

exec 999<"$SCRIPT_HOME" 1001<"$INPUT_DIR"

# Acquire READ-lock on the current directory
flock -sn 999 || { exit 0; }

# Check for a start signal file
startSignal="$(findSignal "start_fuseki_index_")"
[ -n "$startSignal" ] || exit 0 # No start signal found
[ -r "$startSignal" ] || { echo "Could not read '$startSignal'; ERROR"; exit 1; }

# Get an exclusive lock on the input dir to avoid parallel execution
flock -xn 1001 || exit 0

# Parse the run-id from the start-file
RUN_ID="$(grep -i "^Run-Id:" "$startSignal" | cut -d: -f 2 | sed 's/ //g')"
RUN_ID="${RUN_ID:-$(date -u +"%FT%H-%M-%SZ")}"

TARGET_ENV="$(grep -i "^Target-Env:" "$startSignal" | cut -d: -f 2 | sed 's/ //g')"
TARGET_ENV="${TARGET_ENV:-test}"

# Move start signal files to done directory
mkdir -p "$DONE_DIR"
mv "$startSignal" "$DONE_DIR/"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/fuseki_index_${ENV_NAME}_${RUN_ID}.log"

"${SCRIPT_HOME}/create_fuseki_index.sh" "$ENV_NAME" "$RUN_ID" "$TARGET_ENV" >> "$LOG_FILE" 2>&1
