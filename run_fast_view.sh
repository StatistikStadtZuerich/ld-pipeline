#!/bin/bash
set -euo pipefail

SCRIPT="$(readlink -f "$0")"
SCRIPT_ARGS=("$@")
SCRIPT_HOME="$(dirname "$SCRIPT")"
##############################################
_start_signal_prefix="Start_fastview_"
_running_signal_prefix="Running_fastview_"
_done_signal_prefix="Finished_fastview_"
_failed_signal_prefix="Failed_fastview_"
##############################################
load_env() {
  # shellcheck source=sample.env disable=SC2015
  [ -r "$1" ] && . "$1" || true
}
##############################################
ENV_NAME="${1:-local}"
ENV_NAME_UC="$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')"

# load local settings
load_env "${SCRIPT_HOME}/.env"
load_env "${SCRIPT_HOME}/${ENV_NAME}.env"
load_env "./.env"
load_env "./${ENV_NAME}.env"

DROPZONE_BASE=${DROPZONE_BASE:-/home/lod_pipeline/hdb_dropzone}
DROPZONE_DIR=${DROPZONE_DIR:-${DROPZONE_BASE%/}/${ENV_NAME_UC}}
START_SIGNAL_FOLDER="${START_SIGNAL_FOLDER:-${DROPZONE_DIR%/}/Pipeline}"
JENA_DIR="${JENA_DIR:-/home/lod_pipeline/apache-jena-fuseki-4.9.0/jena}"
PIPELINE_DATA_DIR="${PIPELINE_DATA_DIR:-${DROPZONE_DIR%/}/Pipeline_Data}"
VIEW_OUTPUT_DIR="${VIEW_OUTPUT_DIR:-${SCRIPT_HOME%/}/output/triples/preview}"
# Container image carrying the trifid CSV cli
SSZ_VIEW_CSV_IMAGE_TAG="${SSZ_VIEW_CSV_IMAGE_TAG:-latest}"
SSZ_VIEW_CSV_IMAGE="${SSZ_VIEW_CSV_IMAGE:-cmp-registry.stzh.ch/ssz-lod/ld.stadt-zuerich.ch:${SSZ_VIEW_CSV_IMAGE_TAG}}"
CSV_OUTPUT_BASE="${CSV_OUTPUT_BASE:-${DROPZONE_DIR%/}/csv}"
##############################################
debug() {
  if [ "${DEBUG:-false}" = "true" ]; then
    echo "$(date -u +%FT%TZ) ($$) [DEBUG] $*"
  fi
}
findSignal() {
  find "$START_SIGNAL_FOLDER" -maxdepth 1 -type f -name "${1}*.txt" | sort -V | head -1
}
findRunningSignal() {
  findSignal "$_running_signal_prefix"
}
findStartSignal() {
  findSignal "$_start_signal_prefix"
}
loadViewIDs() {
  local config_file="${1:?}"
  [ -f "$config_file" ] || return 1
  <"$config_file" tr ',\n' ' ' | xargs
}
##############################################
runningSignal="$(findRunningSignal)"
[ -z "$runningSignal" ] || { debug "Detected running pipeline: '$runningSignal'; STOP"; exit 0; }

startSignal="$(findStartSignal)"
[ -z "$startSignal" ] && { debug "No start-signal found in '$(readlink -f "$START_SIGNAL_FOLDER")'"; exit 0; }
[ -r "$startSignal" ] || { debug "Could not read start-signal '$startSignal'"; exit 1; }

exec 999<"$SCRIPT_HOME" 1001>>"$startSignal"

# Lock the start-signal for execution
flock -xn 1001 || { debug "Could not acquire exclusive lock on '$startSignal'"; exit 0; }

# Extract the run-id
RUN_ID="$(basename "$startSignal" .txt | sed "s/$_start_signal_prefix//")"

CSV_OUTPUT_DIR="${CSV_OUTPUT_DIR:-${CSV_OUTPUT_BASE%/}/${RUN_ID}}"

# Read the view-ids while the start-signal is still in place
IFS=" " read -r -a VIEW_IDS <<< "$(loadViewIDs "$startSignal")"
# From now on, a read-lock is sufficient
flock -sn 999 || { debug "Could not acquire read-lock"; exit 0; }

debug "Starting ($ENV_NAME) Fast-View Pipeline with runID $RUN_ID"
GIT_REV="$(cd "$SCRIPT_HOME" && git rev-parse HEAD)"
# Make sure we have the correct branch name
branch=$(cd "$SCRIPT_HOME" && git rev-parse --abbrev-ref HEAD)

# Create Running-Signal
_runFile="$START_SIGNAL_FOLDER/${_running_signal_prefix}${RUN_ID}.txt"
cat >"$_runFile" <<EOF
Started: $(date -u +%FT%TZ)
  Run ID: $RUN_ID
  Env: $ENV_NAME
  Branch: $branch
  Git-Rev: $GIT_REV
  VIEW_IDS: ${VIEW_IDS[*]}
EOF

function cleanup() {
  local rc=$?
  [ -z "${FUSEKI_WORK_DIR:-}" ] || rm -rf "$FUSEKI_WORK_DIR"
  if [ "$rc" -ne 0 ] && [ -f "$_runFile" ]; then
    echo "Failed: $(date -u +%FT%TZ) (exit $rc)" >>"$_runFile" || true
    mv -f "$_runFile" "$START_SIGNAL_FOLDER/${_failed_signal_prefix}${RUN_ID}.txt" || true
  fi
  exit "$rc"
}
trap cleanup EXIT

# Move start-signal out of the way - also for a signal without view-ids, so a
# broken signal is not picked up again by the next run.
mkdir -p "$START_SIGNAL_FOLDER/done"
mv "$startSignal" "$START_SIGNAL_FOLDER/done/"
echo "Started: $(date -u +%FT%TZ)" >&1001

[ -n "${VIEW_IDS[*]:-}" ] || { echo "No view-ids found in '$startSignal'" >&2; exit 3; }

export PYENV_VERSION=3.12.1
PY_VENV="${PY_VENV:-/home/lod_pipeline/venv-ld-pipeline-2024/}"

if [ -n "${LD_LIBRARY_PATH:-}" ] && [[ ":$LD_LIBRARY_PATH:" != *":/home/lod_pipeline/openssl_1_1_1/lib:"* ]]; then
  export LD_LIBRARY_PATH="/home/lod_pipeline/openssl_1_1_1/lib:$LD_LIBRARY_PATH"
fi

ARGS=(
  --env "$ENV_NAME"
  --runId "$RUN_ID"
  --config "$SCRIPT_HOME/config.ini"
)
if [ -f "$SCRIPT_HOME/$ENV_NAME.ini" ]; then
  ARGS+=(--config "$SCRIPT_HOME/$ENV_NAME.ini")
fi
if [ -f "$SCRIPT_HOME/config-$ENV_NAME.ini" ]; then
  ARGS+=(--config "$SCRIPT_HOME/config-$ENV_NAME.ini")
fi
ARGS+=(--view-ids "$(IFS=,; echo "${VIEW_IDS[*]}")")

NOTIFY_ARGS=(
  --environment "$ENV_NAME_UC"
  --runId "$RUN_ID"
  --viewIDs "${VIEW_IDS[*]}"
)
"${SCRIPT_HOME:-.}/scripts/teams-notify.sh" fast_view-status --status started --icon "🏎️" --message "Fast-View started" "${NOTIFY_ARGS[@]}"


# Nothing else cleans this folder, so drop leftovers from earlier fast-view runs
# to make sure only the views of this run end up in the index.
if [ -d "$VIEW_OUTPUT_DIR" ]; then
  debug "Removing leftover triples from $VIEW_OUTPUT_DIR"
  find "$VIEW_OUTPUT_DIR" -maxdepth 1 -type f -name '*.ttl.gz' -delete
fi

(
  cd "$SCRIPT_HOME" || { debug "Could not change to '$SCRIPT_HOME'"; exit 2; }
  debug "${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_fast_view.py" "${ARGS[@]}"
  "${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_fast_view.py" "${ARGS[@]}"
) || {
  exit_code="$?"
  "${SCRIPT_HOME:-.}/scripts/teams-notify.sh" fast_view-status --status failed --icon "🚨" --message "Fast-View failed: $exit_code" "${NOTIFY_ARGS[@]}" || true
  exit "${exit_code}"
}

##############################################
# Unpack the embargoed index - it provides the cube data the CSV queries run
# against - and load the freshly generated view definitions into it.
##############################################
# create_fuseki_index.sh names it embargoed_<target-env>_<run-id>.tar.gz
BASE_ARCHIVE="$(find "$PIPELINE_DATA_DIR" -maxdepth 1 -type f -name "embargoed_${ENV_NAME}_*.tar.gz" | sort -V | tail -1)"
[ -n "$BASE_ARCHIVE" ] || { echo "No embargoed index archive for env '$ENV_NAME' found in '$PIPELINE_DATA_DIR'" >&2; exit 4; }

# Collect what the pipeline just generated
TRIPLE_FILES=()
while IFS= read -r -d '' file; do
  TRIPLE_FILES+=("$file")
done < <(find "$VIEW_OUTPUT_DIR" -type f -name '*.ttl.gz' -print0)
if [ "${#TRIPLE_FILES[@]}" -eq 0 ]; then
  echo "No generated triples found in '$VIEW_OUTPUT_DIR' for view id(s) ${VIEW_IDS[*]}" >&2
  exit 5
fi
debug "Found ${#TRIPLE_FILES[@]} generated triple file(s) in $VIEW_OUTPUT_DIR"

debug "Validating the generated triple-files"
RIOT_LOG="$VIEW_OUTPUT_DIR/riot.log"
: > "$RIOT_LOG"
if ! "${JENA_DIR}/bin/riot" --validate "${TRIPLE_FILES[@]}" >>"$RIOT_LOG" 2>&1; then
  debug "Invalid data-files in '$VIEW_OUTPUT_DIR', refuse to build fuseki-index"
  cat "$RIOT_LOG"
  exit 7
fi

# The index is only a scratch artifact for the CSV generation below and is
# removed by the cleanup trap together with the working directory.
FUSEKI_WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fastview_fuseki_${RUN_ID}.XXXX")"
FAST_VIEW_INDEX_LOC="$FUSEKI_WORK_DIR/fastview_${ENV_NAME}_${RUN_ID}"

debug "Unpacking $(basename "$BASE_ARCHIVE") to $FAST_VIEW_INDEX_LOC"
mkdir -p "$FAST_VIEW_INDEX_LOC"
tar -xzf "$BASE_ARCHIVE" --strip-components 1 -C "$FAST_VIEW_INDEX_LOC"

debug "Loading ${#TRIPLE_FILES[@]} file(s) into $FAST_VIEW_INDEX_LOC"
"${JENA_DIR}/bin/tdb2.tdbloader" --loc "$FAST_VIEW_INDEX_LOC" --loader phased "${TRIPLE_FILES[@]}"

debug "Fast-View index ready at $FAST_VIEW_INDEX_LOC"

##############################################
# Generate one CSV per view. The trifid cli runs from its container image
##############################################
# Always fetch the current image - the preview should reflect the latest build.
debug "Pulling $SSZ_VIEW_CSV_IMAGE"
docker pull "$SSZ_VIEW_CSV_IMAGE"

mkdir -p "$CSV_OUTPUT_DIR"

debug "Generating CSVs for ${VIEW_IDS[*]} into $CSV_OUTPUT_DIR"
docker run --rm --network none \
  --hostname localhost \
  --user "$(id -u):$(id -g)" \
  -v "$FAST_VIEW_INDEX_LOC:/index" \
  -v "$CSV_OUTPUT_DIR:/out" \
  "$SSZ_VIEW_CSV_IMAGE" \
  node /app/src/ssz-views/bin/ssz-view-csv.js \
    --endpoint /index \
    --output-dir /out \
    "${VIEW_IDS[@]}"

debug "CSVs written to $CSV_OUTPUT_DIR"

echo "Completed: $(date -u +%FT%TZ)" >>"$_runFile"
mv -f "$_runFile" "$START_SIGNAL_FOLDER/${_done_signal_prefix}${RUN_ID}.txt"
"${SCRIPT_HOME:-.}/scripts/teams-notify.sh" fast_view-status --status finished --icon "🏁" --message "Fast-View finished" "${NOTIFY_ARGS[@]}"
debug "Pipeline run $RUN_ID completed."
