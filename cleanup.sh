#!/bin/bash

ENV_NAME="${1:-local}"
ENV_NAME_UC="$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')"

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

function load_env() {
  [ -r "$1" ] && . "$1" || true
}

# load local settings
load_env "${SCRIPT_HOME}/.env"
load_env "${SCRIPT_HOME}/${ENV_NAME}.env"
load_env "./.env"
load_env "./${ENV_NAME}.env"

JENA_DIR="${JENA_DIR:-/home/lod_pipeline/apache-jena-fuseki-4.9.0/jena}"
FUSEKI_INDEX_DIR="${FUSEKI_INDEX_DIR:-${SCRIPT_HOME%/}/fuseki_index/${ENV_NAME}}"
INPUT_DIR="${INPUT_DIR:-${SCRIPT_HOME%/}/output/${ENV_NAME}}"
DONE_DIR="$INPUT_DIR/done"
DROPZONE_BASE=${DROPZONE_BASE:-/home/lod_pipeline/hdb_dropzone}
DROPZONE_DIR=${DROPZONE_DIR:-${DROPZONE_BASE%/}/${ENV_NAME_UC}}
PIPELINE_DATA_DIR="${PIPELINE_DATA_DIR:-${DROPZONE_DIR%/}/Pipeline_Data}"
LOGS_DIR="${PIPELINE_DATA_DIR:-${DROPZONE_DIR%/}/logs}"

function cleanup_files() {
    local dir="$1"
    local pattern="${2:-*}"
    local days_old="${3:-30}"
    local keep_count="${4:-5}"

    if [ -z "$dir" ]; then
      echo "Usage: $0 <dir> [pattern=$pattern] [days_old=$days_old] [keep_count=$keep_count]" >&2
      return 1
    elif [ ! -d "$dir" ]; then
      echo "Directory not found: '$dir'" >&2
      return 1
    fi

    local files
    files=$(ls -1t "$dir"/$pattern 2>/dev/null)
    
    if [ -n "$files" ]; then
        # Skip the newest <keep_count> files
        echo "$files" | tail -n +"$((keep_count + 1))" | while read -r file; do
            if [ -f "$file" ] && [ -n "$(find "$file" -mtime +"$days_old" -print)" ]; then
                rm "$file"
            fi
        done
    fi
}

# 1) Lösche alle regulären Dateien im Ordner $DONE_DIR, die älter als 24 h sind
find "$DONE_DIR" -type f -mmin +1440 -delete

# 2) Lösche in $FUSEKI_INDEX_DIR nur Dateien/Ordner,
#    die älter als 1 Tag sind, aber nicht den Symlink "current"
#    und nicht dessen Zielverzeichnis.

SYMLINK_PATH="$FUSEKI_INDEX_DIR/current"
if [ -L "$SYMLINK_PATH" ]; then
    TARGET_DIR=$(readlink -f "$SYMLINK_PATH")
else
    TARGET_DIR=""
fi

for ITEM in "$FUSEKI_INDEX_DIR"/*; do
    # Überspringen, wenn es sich um den Symlink oder sein Zielverzeichnis handelt
    if [ "$ITEM" = "$SYMLINK_PATH" ] || [ "$ITEM" = "$TARGET_DIR" ]; then
        continue
    fi

    if find "$ITEM" -prune -mmin +1440 | grep -q .; then
        rm -rf "$ITEM"
    fi
done

# 3) Lösche alle *.tar.gz Dateien in $PIPELINE_DATA_DIR, die älter als 30 Tage sind
#    behalte die 5 neuesten aber immer, egal wie alt sie sind.
cleanup_files "$PIPELINE_DATA_DIR" "*.tar.gz" 30 5
# 4) Cleanup der alten Log-Files (in $LOG_DIR)
#    Alter: 30 Tage, die letzten 7 immer, egal wie alt sie sind.
cleanup_files "$LOGS_DIR" "pipeline_${ENV_NAME}_*.log" 30 7
cleanup_files "$LOGS_DIR" "fuseki_index_${ENV_NAME}_*.log" 30 7

