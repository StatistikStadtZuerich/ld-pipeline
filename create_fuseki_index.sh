#!/usr/bin/env bash
set -e

ENV_NAME="${1:-local}"

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
FUSEKI_INDEX_DIR="${FUSEKI_INDEX_DIR:-/home/lod_pipeline/ld-pipeline-2024/fuseki_index/${ENV_NAME}}"
INPUT_DIR="${INPUT_DIR:-/home/lod_pipeline/ld-pipeline-2024/output/${ENV_NAME}}"
TMP_DIR="$INPUT_DIR/tmp"
DONE_DIR="$INPUT_DIR/done"
CURRENT=current
PIPELINE_DATA_DIR="${PIPELINE_DATA_DIR:-/home/lod_pipeline/hdb_dropzone/prod/test/Pipeline_Data}"

function log() {
    echo "$(date +"%FT%H:%M:%S%Z") $*"
}

# Check for start signal files
START_FILES=("$INPUT_DIR"/start_fuseki_index_*.txt)
if [ -e "${START_FILES[0]}" ]; then
    log "Start signal file(s) found. Beginning process for $ENV_NAME."
else
    # log "No start signal file(s) found in $INPUT_DIR. Exiting."
    exit 0
fi

# Move start signal files to done directory
for START_FILE in "${START_FILES[@]}"; do
    if [ -e "$START_FILE" ]; then
        log "Moving $START_FILE to $DONE_DIR"
        mkdir -p "$DONE_DIR"
        mv "$START_FILE" "$DONE_DIR/"
    fi
done

log "Starting process for all .gz files in $INPUT_DIR"

mkdir -p "$FUSEKI_INDEX_DIR"
VERSION="$(date +"%F_%H-%M-%S_%Z")"
DATA_DIR="$FUSEKI_INDEX_DIR/$VERSION"

# Get the current date and time for the filename
CURRENT_DATETIME=$(date +"%Y%m%d%H%M%S")
FINAL_COMBINED_FILE="$TMP_DIR/${ENV_NAME}_combined_${CURRENT_DATETIME}.ttl.gz"

# Move all .gz files from the input to the temporary directory
for FILE in "$INPUT_DIR"/*.gz; do
    if [ -r "$FILE" ]; then
        log "Moving $FILE to $TMP_DIR"
        mkdir -p "$TMP_DIR"
        mv "$FILE" "$TMP_DIR/"
    else
        log "No readable .gz files found in $INPUT_DIR, skipping"
    fi
done

# Combine all .gz files into a single .ttl file and then compress it into a single .gz file
log "Combining all .gz files into a single gz file"
gunzip -c "$TMP_DIR"/*.gz > "$TMP_DIR/${ENV_NAME}_combined_${CURRENT_DATETIME}.ttl" \
  || { log "Failed to combine .gz files" >&2; exit 2; }
gzip -c "$TMP_DIR/${ENV_NAME}_combined_${CURRENT_DATETIME}.ttl" > "$FINAL_COMBINED_FILE" \
  || { log "Failed to compress combined .ttl file" >&2; exit 2; }
log "Final combined file created: $FINAL_COMBINED_FILE"

# Load the final combined .ttl.gz file with tdb2.xloader
log "Starting import of $FINAL_COMBINED_FILE into $DATA_DIR"
"${JENA_DIR}/bin/tdb2.xloader" --loc "$DATA_DIR" "$FINAL_COMBINED_FILE" \
  || { log "Import failed for $FINAL_COMBINED_FILE" >&2; exit 2; }
log "Import complete for $FINAL_COMBINED_FILE"

# Move processed file to the done directory
log "Moving $FINAL_COMBINED_FILE to $DONE_DIR"
mv "$FINAL_COMBINED_FILE" "$DONE_DIR/"

# TODO: Execute Warmup-Phase here

# Generate statistics and place in correct location
log "Generating statistics file for $DATA_DIR"
TMP_STATS_FILE="/tmp/stats_${CURRENT_DATETIME}.opt"
"${JENA_DIR}/bin/tdb2.tdbstats" --loc="$DATA_DIR" > "$TMP_STATS_FILE" \
  || { log "tdb2.tdbstats failed" >&2; exit 2; }

STATS_PIPELINE_DATA_DIR="$DATA_DIR/Data-0001"
if [ -d "$STATS_PIPELINE_DATA_DIR" ]; then
    log "Moving stats file to $STATS_PIPELINE_DATA_DIR"
    mv "$TMP_STATS_FILE" "$STATS_PIPELINE_DATA_DIR/stats.opt" \
      || { log "Failed to move stats file" >&2; exit 2; }
    log "Statistics file created: $STATS_PIPELINE_DATA_DIR/stats.opt"
else
    log "Target directory $STATS_PIPELINE_DATA_DIR not found, skipping stats.opt move"
    rm -f "$TMP_STATS_FILE"
fi

# Clean up temporary directory
log "Cleaning up temporary directory"
rm -f "$TMP_DIR"/*.gz "$TMP_DIR/${ENV_NAME}_combined_${CURRENT_DATETIME}.ttl"

# Update 'current' symlink after processing all files
(
    log "Updating '${CURRENT}' symlink"
    cd "$FUSEKI_INDEX_DIR" || { log "Could not cd to $FUSEKI_INDEX_DIR, exit" >&2; exit 2; }
    [ -L "${CURRENT}" ] && rm -f "${CURRENT}"
    ln -s "$VERSION" "${CURRENT}"
    log "$FUSEKI_INDEX_DIR/${CURRENT} -> $FUSEKI_INDEX_DIR/$VERSION"
)

# Compress the current directory to a tar.gz file
log "Compressing the current directory to a tar.gz file"
CURRENT_DIR="${FUSEKI_INDEX_DIR}/${CURRENT}"
TAR_FILE="${FUSEKI_INDEX_DIR}/${ENV_NAME}_${CURRENT_DATETIME}.tar.gz"

tar -czf "$TAR_FILE" -C "$FUSEKI_INDEX_DIR" "$VERSION" \
  || { log "Failed to create tar file for $CURRENT_DIR" >&2; exit 2; }
log "Compressed tar file created: $TAR_FILE"

# Copy the .tar.gz file to the target directory
log "Copying $TAR_FILE to $PIPELINE_DATA_DIR"
cp "$TAR_FILE" "$PIPELINE_DATA_DIR" || { log "Failed to copy $TAR_FILE to $PIPELINE_DATA_DIR" >&2; exit 2; }
log "File successfully copied to $PIPELINE_DATA_DIR"

log "All files processed and import complete"
