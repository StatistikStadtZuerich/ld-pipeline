#!/usr/bin/env bash

JENA_DIR="${JENA_DIR:-/home/lod_pipeline/apache-jena-fuseki-4.9.0/jena}"
DATA_ROOT="${DATA_ROOT:-/home/lod_pipeline/ld-pipeline-2024/fuseki_index/int}"
INPUT_DIR="/home/lod_pipeline/ld-pipeline-2024/output/int"
TMP_DIR="$INPUT_DIR/tmp"
DONE_DIR="$INPUT_DIR/done"
CURRENT=current
TARGET_DIR="/home/lod_pipeline/hdb_dropzone/prod/test/Pipeline_Data"

function log() {
    echo "$(date +"%FT%H:%M:%S%Z") $*"
}

VERSION="$(date +"%F_%H-%M-%S_%Z")"
DATA_DIR="$DATA_ROOT/$VERSION"

# Get the current date and time for the filename
CURRENT_DATETIME=$(date +"%Y%m%d%H%M%S")
FINAL_COMBINED_FILE="$TMP_DIR/int_combined_${CURRENT_DATETIME}.ttl.gz"

# Check for start signal files
START_FILES=("$INPUT_DIR"/start_fuseki_index_*.txt)
if [ -e "${START_FILES[0]}" ]; then
    log "Start signal file(s) found. Beginning process."
else
    # log "No start signal file(s) found in $INPUT_DIR. Exiting."
    exit 0
fi

# Move start signal files to done directory
for START_FILE in "${START_FILES[@]}"; do
    if [ -e "$START_FILE" ]; then
        log "Moving $START_FILE to $DONE_DIR"
        mv "$START_FILE" "$DONE_DIR/"
    fi
done

log "Starting process for all .gz files in $INPUT_DIR"

# Move all .gz files from the input to the temporary directory
for FILE in "$INPUT_DIR"/*.gz; do
    if [ -r "$FILE" ]; then
        log "Moving $FILE to $TMP_DIR"
        mv "$FILE" "$TMP_DIR/"
    else
        log "No readable .gz files found in $INPUT_DIR, skipping"
    fi
done

# Combine all .gz files into a single .ttl file and then compress it into a single .gz file
log "Combining all .gz files into a single gz file"
gunzip -c "$TMP_DIR"/*.gz > "$TMP_DIR/int_combined_${CURRENT_DATETIME}.ttl" || { log "Failed to combine .gz files" >&2; exit 2; }
gzip -c "$TMP_DIR/int_combined_${CURRENT_DATETIME}.ttl" > "$FINAL_COMBINED_FILE" || { log "Failed to compress combined .ttl file" >&2; exit 2; }
log "Final combined file created: $FINAL_COMBINED_FILE"

# Load the final combined .ttl.gz file with tdb2.xloader
log "Starting import of $FINAL_COMBINED_FILE into $DATA_DIR"
"${JENA_DIR}/bin/tdb2.xloader" --loc "$DATA_DIR" "$FINAL_COMBINED_FILE" || { log "Import failed for $FINAL_COMBINED_FILE" >&2; exit 2; }
log "Import complete for $FINAL_COMBINED_FILE"

# Move processed file to the done directory
log "Moving $FINAL_COMBINED_FILE to $DONE_DIR"
mv "$FINAL_COMBINED_FILE" "$DONE_DIR/"

# Generate statistics and place in correct location
log "Generating statistics file for $DATA_DIR"
TMP_STATS_FILE="/tmp/stats_${CURRENT_DATETIME}.opt"
"${JENA_DIR}/bin/tdb2.tdbstats" --loc="$DATA_DIR" > "$TMP_STATS_FILE" || { log "tdb2.tdbstats failed" >&2; exit 2; }

STATS_TARGET_DIR="$DATA_DIR/Data-0001"
if [ -d "$STATS_TARGET_DIR" ]; then
    log "Moving stats file to $STATS_TARGET_DIR"
    mv "$TMP_STATS_FILE" "$STATS_TARGET_DIR/stats.opt" || { log "Failed to move stats file" >&2; exit 2; }
    log "Statistics file created: $STATS_TARGET_DIR/stats.opt"
else
    log "Target directory $STATS_TARGET_DIR not found, skipping stats.opt move"
fi

# Clean up temporary directory
log "Cleaning up temporary directory"
rm -f "$TMP_DIR"/*.gz "$TMP_DIR/int_combined_${CURRENT_DATETIME}.ttl"

# Update 'current' symlink after processing all files
(
    log "Updating '${CURRENT}' symlink"
    cd "$DATA_ROOT" || { log "Could not cd to $DATA_ROOT, exit" >&2; exit 2; }
    [ -L "${CURRENT}" ] && rm -f "${CURRENT}"
    ln -s "$VERSION" "${CURRENT}"
    log "$DATA_ROOT/${CURRENT} -> $DATA_ROOT/$VERSION"
)

# Compress the current directory to a tar.gz file
log "Compressing the current directory to a tar.gz file"
CURRENT_DIR="${DATA_ROOT}/${CURRENT}"
TAR_FILE="/home/lod_pipeline/ld-pipeline-2024/fuseki_index/int/int_${CURRENT_DATETIME}.tar.gz"

tar -czf "$TAR_FILE" -C "$DATA_ROOT" "$VERSION" || { log "Failed to create tar file for $CURRENT_DIR" >&2; exit 2; }
log "Compressed tar file created: $TAR_FILE"

# Copy the .tar.gz file to the target directory
log "Copying $TAR_FILE to $TARGET_DIR"
cp "$TAR_FILE" "$TARGET_DIR" || { log "Failed to copy $TAR_FILE to $TARGET_DIR" >&2; exit 2; }
log "File successfully copied to $TARGET_DIR"

log "All files processed and import complete"
