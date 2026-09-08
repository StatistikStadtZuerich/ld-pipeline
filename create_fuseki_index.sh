#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

ENV_NAME="${1:-local}"
ENV_NAME_UC="$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')"
RUN_ID="${2:-$(date -u +"%FT%H-%M-%SZ")}"
TARGET_ENV="${3:-test}"

# Those ENVs should be passed by the calling script
JENA_DIR="${JENA_DIR:-/home/lod_pipeline/apache-jena-fuseki-4.9.0/jena}"
FUSEKI_INDEX_DIR="${FUSEKI_INDEX_DIR:-${SCRIPT_HOME%/}/fuseki_index/${TARGET_ENV}}"
INPUT_DIR="${INPUT_DIR:-${SCRIPT_HOME%/}/output/${ENV_NAME}}"
DROPZONE_BASE=${DROPZONE_BASE:-/home/lod_pipeline/hdb_dropzone}
DROPZONE_DIR=${DROPZONE_DIR:-${DROPZONE_BASE%/}/${ENV_NAME_UC}}
PIPELINE_DATA_DIR="${PIPELINE_DATA_DIR:-${DROPZONE_DIR%/}/Pipeline_Data}"

TMP_DIR="$INPUT_DIR/tmp"
DONE_DIR="$INPUT_DIR/done"
CURRENT=current

OUTPUT_TYPES=(shared public embargoed)

function log() {
    echo "$(date -u +%FT%TZ) $*"
}
log "Start building Fuseki-Index for '$TARGET_ENV' with Run-ID '$RUN_ID' to '$FUSEKI_INDEX_DIR'"

mkdir -p "$FUSEKI_INDEX_DIR"
VERSION="$(date +"%F_%H-%M-%S_%Z")"
DATA_DIR="$FUSEKI_INDEX_DIR/$VERSION"

VERSION_DIR="$FUSEKI_INDEX_DIR/$VERSION"
SHARED_DIR="$VERSION_DIR/shared"

mkdir -p "$VERSION_DIR" "$SHARED_DIR"

declare -A INDEX_DIR
# Get the current date and time for the filename
CURRENT_DATETIME=$(date +"%Y%m%d%H%M%S")
FINAL_COMBINED_FILE="$TMP_DIR/${TARGET_ENV}_combined_${CURRENT_DATETIME}.ttl.gz"

log "Loading all .gz files in $INPUT_DIR"
# Move all .gz files from the input to the temporary directory
rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"

AVAILABLE_TYPES=()
for TYPE in "${OUTPUT_TYPES[@]}"; do
  SRC="$INPUT_DIR/$TYPE"
  FILES=("$SRC"/*.gz)

  if [ ${#FILES[@]} -eq 0 ]; then
    log "Typ '$TYPE': No readable .gz files found in $SRC, skipping"
    continue
  fi

  mkdir -p "$TMP_DIR/$TYPE"
  log "Typ '$TYPE': Moving ${#FILES[@]} files"
  mv "${FILES[@]}" "$TMP_DIR/$TYPE/"
  AVAILABLE_TYPES+=("$TYPE")
done

if [ ! -d "$TMP_DIR/shared" ]; then
  log "No 'shared'-Files found, abort" >&2
  exit 3
fi

# Validate all the input files
RIOT_LOG="$TMP_DIR/riot.log"
: > "$RIOT_LOG"

for TYPE in "${AVAILABLE_TYPES[@]}"; do
  log "Validating data-files in '$TMP_DIR/$TYPE', details will be reported to $RIOT_LOG"
  if ! "${JENA_DIR}/bin/riot" --validate "$TMP_DIR/$TYPE"/*.gz &>>"$RIOT_LOG"; then
    log "Invalid data-files in '$TMP_DIR/$TYPE', refuse to build fuseki-index"
    cat "$RIOT_LOG"
    exit 3
  fi
done

declare -A COMBINED_FILE

for TYPE in "${AVAILABLE_TYPES[@]}"; do
  PLAIN="$TMP_DIR/${TARGET_ENV}_${TYPE}_${CURRENT_DATETIME}.ttl"
  PACKED="${PLAIN}.gz"

  log "Combining all .gz files f type '$TYPE' into a single gz file"
  gunzip -c "$TMP_DIR/$TYPE"/*.gz > "$PLAIN" \
    || { log "Failed to combine .gz files for type '$TYPE'" >&2; exit 2; }
  gzip -c "$PLAIN" > "$PACKED" \
    || { log "Failed to compress combined .ttl file for type '$TYPE'" >&2; exit 2; }
  rm -f "$PLAIN"

  COMBINED_FILE["$TYPE"]="$PACKED"
  log "Combined file created for type '$TYPE': $PACKED"
done

# TODO:
# 1. Create the Base-Archive
# 2. Load the public observations
#    - add the stats-file
#    - create the public Fuseki-Index
#    - copy the public Index to HDB Dropzone
# 3. Load the embargoed observations (into the Base Archive)
#    - add the stats-file
#    - create the embargoed Fuseki-Index

log "Building base archive from shared data"
"${JENA_DIR}/bin/tdb2.xloader" --loc "$BASE_DIR" "${COMBINED_FILE[shared]}" \
   || { log "xloader failed for shared data" >&2; exit 2; }
log "Base archive complete"

if [ -n "${COMBINED_FILE[public]:-}" ]; then
  PUBLIC_DIR="$VERSION_DIR/public"
  log "Copying base archive to $PUBLIC_DIR"
  cp -a "$BASE_DIR" "$PUBLIC_DIR" \
     || { log "Failed to copy base archive for public index" >&2; exit 2; }

  log "Base archive copied to $PUBLIC_DIR"
  "${JENA_DIR}/bin/tdb2.tbdloader" --loc "$PUBLIC_DIR" "${COMBINED_FILE[public]}" \
     || { log "tdb2.tbdloader failed for public data" >&2; exit 2; }

  INDEX_DIR[public]="$PUBLIC_DIR"
  log "Public index complete"
else
  log "No public data, skipping public index"
fi

if [ -n "${COMBINED_FILE[embargoed]:-}" ]; then
  EMBARGOED_DIR="$VERSION_DIR/embargoed"
  SOURCE_DIR="${INDEX_DIR[public]:-$BASE_DIR}"

  log "Copying $SOURCE_DIR to $EMBARGOED_DIR"
  cp -a "$SOURCE_DIR" "$EMBARGOED_DIR" \
     || { log "Failed to copy base archive for embargoed index" >&2; exit 2; }

  log "Loading embargoed data into $EMBARGOED_DIR"
  "${JENA_DIR}/bin/tdb2.tbdloader" --loc "$EMBARGOED_DIR" "${COMBINED_FILE[embargoed]}" \
     || { log "tdb2.tbdloader failed for embargoed data" >&2; exit 2; }
  INDEX_DIR[embargoed]="$EMBARGOED_DIR"
  log "Embargoed index complete"
else
  log "No embargoed data, skipping embargoed index"
fi

# Move processed file to the done directory
mkdir -p "$DONE_DIR"
log "Moving $FINAL_COMBINED_FILE to $DONE_DIR"
mv "$FINAL_COMBINED_FILE" "$DONE_DIR/"

# TODO: Execute Warmup-Phase here

declare -A ARCHIVE_FILE
# Generate statistics and place in correct location
finalize_index() {
  local type="$1"
  local data_dir="$2"
  local stats_dir="$data_dir/Data-0001"
  local tmp_stats="/tmp/stats_${type}_${CURRENT_DATETIME}.opt"

  log "Generating statistics for $type"
  "${JENA_DIR}/bin/tdb2.tdbstats" --loc="$data_dir" > "$tmp_stats" \
    || { log "tdb2.tdbstats failed for $type" >&2; exit 1; }

  if [ -d "$stats_dir" ]; then
    mv "$tmp_stats" "$stats_dir/stats.opt" \
      || { log "Failed to move stats file for $type" >&2; exit 1; }
    log "Statistics file created for $type: $stats_dir/stats.opt"
  else
    log "Target directory $stats_dir not found for $type, skipping stats.opt move"
    rm -f "$tmp_stats"
  fi

  local archive_name="${TARGET_ENV}_${type}_${CURRENT_DATETIME}.tar.gz"

  log "Creating archive $archive_name"
  tar -czf "$FUSEKI_INDEX_DIR/$archive_name" -C "$FUSEKI_INDEX_DIR" "$VERSION/$type" \
    || { log "Failed to create archive for $type" >&2; exit 1; }
  ARCHIVE_FILE["$type"]="$archive_name"
}

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
ARCHIVE_FILE_NAME="${TARGET_ENV}_${CURRENT_DATETIME}.tar.gz"
TAR_FILE="${FUSEKI_INDEX_DIR}/${ARCHIVE_FILE_NAME}"

tar -czf "$TAR_FILE" -C "$FUSEKI_INDEX_DIR" "$VERSION" \
  || { log "Failed to create tar file for $CURRENT_DIR" >&2; exit 2; }
log "Compressed tar file created: $TAR_FILE"

# Copy the .tar.gz file to the target directory
log "Copying $TAR_FILE to $PIPELINE_DATA_DIR"
(
  mkdir -p "${PIPELINE_DATA_DIR}"
  cp "$TAR_FILE" "${PIPELINE_DATA_DIR}/${ARCHIVE_FILE_NAME}.tmp" \
    && mv "${PIPELINE_DATA_DIR}/${ARCHIVE_FILE_NAME}.tmp" "${PIPELINE_DATA_DIR}/${ARCHIVE_FILE_NAME}"
) || { log "Failed to copy $TAR_FILE to $PIPELINE_DATA_DIR" >&2; exit 2; }
log "File successfully copied to $PIPELINE_DATA_DIR"

"${SCRIPT_HOME:-.}/scripts/teams-notify.sh" index-created \
  --sourceEnv "$(echo "${ENV_NAME}" | tr '[:lower:]' '[:upper:]')" \
  --targetEnv "$(echo "${TARGET_ENV}" | tr '[:lower:]' '[:upper:]')" \
  --archive "$(basename "$TAR_FILE")"
log "All files processed and import complete"
