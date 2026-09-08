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

function log() {
    echo "$(date -u +%FT%TZ) $*"
}
function create_fuseki_index() {
    local index_dir="${1:?}"
    local ttl_source_dir="${2:?}"

    index_dir="${index_dir%/}"

    mkdir -p "$index_dir"
    if [ -f "$index_dir/tdb.lock" ]; then
      log "tdb.lock found in $index_dir, using incremental load"
      find "$ttl_source_dir" -type f -name '*.ttl.gz' -print0 \
        | xargs -r -0 "${JENA_DIR}/bin/tdb2.tdbloader" --loc "$index_dir" \
        || { log "tdb2.tdbloader failed to load $ttl_source_dir into $index_dir data" >&2; return 2; }
    else
      log "$index_dir seems empty, using xloader"
      find "$ttl_source_dir" -type f -name '*.ttl.gz' -print0 \
        | xargs -r -0 "${JENA_DIR}/bin/tdb2.xloader" --loc "$index_dir" \
        || { log "tdb2.xloader failed to create $index_dir from $ttl_source_dir" >&2; return 2; }
    fi

    log "loading complete, generating stats"
    local tmp_stats="$index_dir/stats.tmp"
    local stats_dir="$index_dir/Data-0001"
    "${JENA_DIR}/bin/tdb2.tdbstats" --loc="$index_dir" > "$tmp_stats" \
        || { log "tdb2.tdbstats failed in $index_dir" >&2; return 1; }

    if [ -d "$stats_dir" ]; then
      mv -f "$tmp_stats" "$stats_dir/stats.opt" \
        || { log "Failed to move stats file to $stats_dir" >&2; exit 1; }
      log "Statistics file created: $stats_dir/stats.opt"
    else
      log "Target directory $stats_dir not found in $index_dir, skipping stats.opt move"
      rm -f "$tmp_stats"
    fi
}
function compress_fuseki_index() {
    local base_dir="${1:?}"
    local index_name="${2:?}"
    local target_dir="${3:?}"

    base_dir=${base_dir%/}
    target_dir=${target_dir%/}

    [ -d "$base_dir/$index_name" ] || { log "No Fuseki-Index at $base_dir/$index_name found"; return 1; }
    local archive="${index_name}.tar.gz"
    log "Creating $archive from $base_dir/$index_name"
    mkdir -p "$target_dir"
    tar -czf "$target_dir/$archive" -C "$base_dir" "$index_name" \
      || { log "Failed to create $archive from $base_dir/$index_name"; return 1; }
    log "Created archive $target_dir/$archive"
}
function unpack_fuseki_archive() {
    local archive="${1:?}"
    local target_dir="${2:?}"

    [ -f "$archive" ] || { log "Can't read Fuseki-Archive $archive"; return 1; }
    log "Unpacking $(basename "$archive") to $target_dir"
    mkdir -p "$target_dir"
    tar -xzf "$archive" --strip-components 1 -C "$target_dir" \
      || { log "Failed to unpack $(basename "$archive") to $target_dir" >&2; return 1; }
    log "Unpacked $(basename "$archive") to $target_dir"
}
function run_data_tests() {
    local fuseki_loc="${1:?}"
    log "TODO: Run Data-Tests on $fuseki_loc"
}
function secure_copy() {
    local source="$1"
    local target_dir="$2"
    local temp

    (
      mkdir -p "$target_dir"
      temp="$(mktemp -p "$target_dir")"
      cp -f "$source" "$temp" \
        && mv "$temp" "$target_dir/$(basename "$source")"
    ) || { log "Failed to copy $source to $target_dir" >&2; return 2; }
  log "$source successfully copied to $target_dir"
}

log "Start building Fuseki-Index for '$TARGET_ENV' with Run-ID '$RUN_ID' to '$FUSEKI_INDEX_DIR'"
WORKING_DIR="$(mktemp -d -t "fuseki_$RUN_ID")"
trap 'rm -rf "$WORKING_DIR"' EXIT

log "Moving Data-Input to the Working-Dir at $WORKING_DIR"
mkdir -p "$WORKING_DIR/input"
mv "$INPUT_DIR"/* "$WORKING_DIR/input/"

INPUT_FILES=()
while IFS= read -r -d '' file; do
  INPUT_FILES+=("$file")
done < <(find "$WORKING_DIR/input" -type f -name '*.ttl.gz' -print0)

if [ "${#INPUT_FILES[@]}" -eq 0 ]; then
  log "No .ttl.gz input files found in $INPUT_DIR" >&2
  exit 3
fi
log "Found ${#INPUT_FILES[@]} input files in $INPUT_DIR"

# Validate all the input files
log "Validating the input-files"
RIOT_LOG="$WORKING_DIR/riot.log"
: > "$RIOT_LOG"
if ! "${JENA_DIR}/bin/riot" --validate "${INPUT_FILES[@]}" &>>"$RIOT_LOG"; then
  log "Invalid data-files in '$WORKING_DIR/input', refuse to build fuseki-index"
  cat "$RIOT_LOG"
  trap - EXIT
  exit 3
fi

log "Building base archive from shared data"
FUSEKI_BASE="$WORKING_DIR/fuseki"
mkdir -p "$FUSEKI_BASE"

INDEXES=()

[ -d "$WORKING_DIR/input/shared" ] || { log "Missing shared input directory"; exit 3; }
BASE_INDEX="base_${TARGET_ENV}_${RUN_ID}"
create_fuseki_index "$FUSEKI_BASE/$BASE_INDEX" "$WORKING_DIR/input/shared"
compress_fuseki_index "$FUSEKI_BASE" "$BASE_INDEX" "$FUSEKI_INDEX_DIR"
log "Base-Archive built: $BASE_INDEX ($BASE_INDEX.tar.gz)"
INDEXES+=("$BASE_INDEX")

if [ -d "$WORKING_DIR/input/public" ]; then
  log "Building Public Index"
  PUBLIC_INDEX="${TARGET_ENV}_${RUN_ID}"
  mv "$FUSEKI_BASE/$BASE_INDEX" "$FUSEKI_BASE/$PUBLIC_INDEX"
  create_fuseki_index "$FUSEKI_BASE/$PUBLIC_INDEX" "$WORKING_DIR/input/public"
  run_data_tests "$FUSEKI_BASE/$PUBLIC_INDEX"
  compress_fuseki_index "$FUSEKI_BASE" "$PUBLIC_INDEX" "$FUSEKI_INDEX_DIR"
  rm -rf "${FUSEKI_BASE:?}/$PUBLIC_INDEX"
  log "Public Index built: $PUBLIC_INDEX ($PUBLIC_INDEX.tar.gz)"
  INDEXES+=("$PUBLIC_INDEX")
else
  rm -rf "${FUSEKI_BASE:?}/$BASE_INDEX"
  log "Missing public input directory, will not create public index"
fi

if [ -d "$WORKING_DIR/input/embargoed" ]; then
  log "Building Preview Index with embargoed Data"
  PREVIEW_INDEX="embargoed_${TARGET_ENV}_${RUN_ID}"
  unpack_fuseki_archive "$FUSEKI_INDEX_DIR/$BASE_INDEX.tar.gz" "$FUSEKI_BASE/$PREVIEW_INDEX"
  create_fuseki_index "$FUSEKI_BASE/$PREVIEW_INDEX" "$WORKING_DIR/input/embargoed"
  run_data_tests "$FUSEKI_BASE/$PREVIEW_INDEX"
  compress_fuseki_index "$FUSEKI_BASE" "$PREVIEW_INDEX" "$FUSEKI_INDEX_DIR"
  log "Preview Index built: $PREVIEW_INDEX ($PREVIEW_INDEX.tar.gz)"
  INDEXES+=("$PREVIEW_INDEX")
else
  log "Missing embargoed input directory, will not create preview/embargoed index"
fi

log "Copying Archives to Dropzone"
for a in "${INDEXES[@]}"; do
  log "Copy $a to $PIPELINE_DATA_DIR"
  secure_copy "$FUSEKI_INDEX_DIR/$a.tar.gz" "$PIPELINE_DATA_DIR"
  log "$a copied to $PIPELINE_DATA_DIR"
done

if [ -n "${PUBLIC_INDEX:-}" ]; then
  "${SCRIPT_HOME:-.}/scripts/teams-notify.sh" index-created \
    --sourceEnv "$(echo "${ENV_NAME}" | tr '[:lower:]' '[:upper:]')" \
    --targetEnv "$(echo "${TARGET_ENV}" | tr '[:lower:]' '[:upper:]')" \
    --archive "$PUBLIC_INDEX.tar.gz"
else
  log "No public index was created, skipping index-created notification"
fi

log "All files processed and import complete"
