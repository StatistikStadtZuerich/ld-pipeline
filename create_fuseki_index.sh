#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

ENV_NAME="${1:-local}"
RUN_ID="${2:-$(date -u +"%FT%H-%M-%SZ")}"
TARGET_ENV="${3:-test}"

# Those ENVs should be passed by the calling script
JENA_DIR="${JENA_DIR:-/home/lod_pipeline/apache-jena-fuseki-4.9.0/jena}"
FUSEKI_INDEX_DIR="${FUSEKI_INDEX_DIR:-/home/lod_pipeline/ld-pipeline-2024/fuseki_index/${TARGET_ENV}}"
INPUT_DIR="${INPUT_DIR:-/home/lod_pipeline/ld-pipeline-2024/output/${ENV_NAME}}"
PIPELINE_DATA_DIR="${PIPELINE_DATA_DIR:-/home/lod_pipeline/hdb_dropzone/prod/test/Pipeline_Data}"

TMP_DIR="$INPUT_DIR/tmp"
DONE_DIR="$INPUT_DIR/done"
CURRENT=current

function log() {
    echo "$(date -u +%FT%TZ) $*"
}
log "Start building Fuseki-Index for '$TARGET_ENV' with Run-ID '$RUN_ID' to '$FUSEKI_INDEX_DIR'"

mkdir -p "$FUSEKI_INDEX_DIR"
VERSION="$(date +"%F_%H-%M-%S_%Z")"
DATA_DIR="$FUSEKI_INDEX_DIR/$VERSION"

# Get the current date and time for the filename
CURRENT_DATETIME=$(date +"%Y%m%d%H%M%S")
FINAL_COMBINED_FILE="$TMP_DIR/${TARGET_ENV}_combined_${CURRENT_DATETIME}.ttl.gz"

log "Loading all .gz files in $INPUT_DIR"
# Move all .gz files from the input to the temporary directory
rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"
for FILE in "$INPUT_DIR"/*.gz; do
    [ -e "$FILE" ] || continue
    if [ -r "$FILE" ]; then
        log "Moving $FILE to $TMP_DIR"
        mv "$FILE" "$TMP_DIR/"
    else
        log "No readable .gz files found in $INPUT_DIR, skipping"
    fi
done

# Validate all the input files
RIOT_LOG="$TMP_DIR/riot.log"
if ! "${JENA_DIR}/bin/riot" --validate "$TMP_DIR"/*.gz &>"$RIOT_LOG"; then
  log "Invalid data-files, refuse to build fuseki-index"
  cat "$RIOT_LOG"
  exit 3
fi

# Combine all .gz files into a single .ttl file and then compress it into a single .gz file
log "Combining all .gz files into a single gz file"
gunzip -c "$TMP_DIR"/*.gz > "$TMP_DIR/${TARGET_ENV}_combined_${CURRENT_DATETIME}.ttl" \
  || { log "Failed to combine .gz files" >&2; exit 2; }
gzip -c "$TMP_DIR/${TARGET_ENV}_combined_${CURRENT_DATETIME}.ttl" > "$FINAL_COMBINED_FILE" \
  || { log "Failed to compress combined .ttl file" >&2; exit 2; }
log "Final combined file created: $FINAL_COMBINED_FILE"

# Load the final combined .ttl.gz file with tdb2.xloader
log "Starting import of $FINAL_COMBINED_FILE into $DATA_DIR"
"${JENA_DIR}/bin/tdb2.xloader" --loc "$DATA_DIR" "$FINAL_COMBINED_FILE" \
  || { log "Import failed for $FINAL_COMBINED_FILE" >&2; exit 2; }
log "Import complete for $FINAL_COMBINED_FILE"

# Move processed file to the done directory
mkdir -p "$DONE_DIR"
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
rm -f "$TMP_DIR"/*.gz "$TMP_DIR/${TARGET_ENV}_combined_${CURRENT_DATETIME}.ttl"

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
TAR_FILE="${FUSEKI_INDEX_DIR}/${TARGET_ENV}_${CURRENT_DATETIME}.tar.gz"

tar -czf "$TAR_FILE" -C "$FUSEKI_INDEX_DIR" "$VERSION" \
  || { log "Failed to create tar file for $CURRENT_DIR" >&2; exit 2; }
log "Compressed tar file created: $TAR_FILE"

# Copy the .tar.gz file to the target directory
log "Copying $TAR_FILE to $PIPELINE_DATA_DIR"
cp "$TAR_FILE" "$PIPELINE_DATA_DIR" || { log "Failed to copy $TAR_FILE to $PIPELINE_DATA_DIR" >&2; exit 2; }
log "File successfully copied to $PIPELINE_DATA_DIR"

"${SCRIPT_HOME:-.}/scripts/teams-notify.sh" index-created \
  --sourceEnv "$(echo "${ENV_NAME}" | tr '[:lower:]' '[:upper:]')" \
  --targetEnv "$(echo "${TARGET_ENV}" | tr '[:lower:]' '[:upper:]')" \
  --archive "$(basename "$TAR_FILE")"
log "All files processed and import complete"
