#!/bin/bash
set -euo pipefail

SCRIPT="$(readlink -f "$0")"
SCRIPT_ARGS=("$@")
SCRIPT_HOME="$(dirname "$SCRIPT")"
##############################################
_start_signal_prefix="Start_fastview_"
_running_signal_prefix="Running_fastview_"
_done_signal_prefix="Finished_fastview_"
##############################################
ENV_NAME="${1:-local}"
ENV_NAME_UC="$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')"
DROPZONE_BASE=${DROPZONE_BASE:-/home/lod_pipeline/hdb_dropzone}
DROPZONE_DIR=${DROPZONE_DIR:-${DROPZONE_BASE%/}/${ENV_NAME_UC}}
START_SIGNAL_FOLDER="${START_SIGNAL_FOLDER:-${DROPZONE_DIR%/}/Pipeline}"
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
EOF
# Move start-signal out of the way
mkdir -p "$START_SIGNAL_FOLDER/done"
mv "$startSignal" "$START_SIGNAL_FOLDER/done/"
echo "Started: $(date -u +%FT%TZ)" >&1001

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

IFS=" " read -r -a VIEW_IDS <<< "$(loadViewIDs "$startSignal")"

NOTIFY_ARGS=(
  --environment "$ENV_NAME_UC"
  --runId "$RUN_ID"
  --viewIDs "${VIEW_IDS[*]}"
)
"${SCRIPT_HOME:-.}/scripts/teams-notify.sh" fast_view-status --status started --icon "🏎️" --message "Fast-View started" "${NOTIFY_ARGS[@]}"
(
  cd "$SCRIPT_HOME" || { debug "Could not change to '$SCRIPT_HOME'"; exit 2; }
  debug "${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_fast_view.py" "${ARGS[@]}"
  "${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_fast_view.py" "${ARGS[@]}"
) || {
  exit_code="$?"
  "${SCRIPT_HOME:-.}/scripts/teams-notify.sh" fast_view-error --status failed --icon "🚨" --message "Fast-View failed: $exit_code"  "${NOTIFY_ARGS[@]}"
  exit "${exit_code}"
}

# TODO: Use the correct index for fuseki (archive with embargoed data) and load the generated triples

# TODO: Use the algorithm from trifid (ld-stzh-ch) to generate the CSVs for all $VIEW_IDS

echo "Completed: $(date -u +%FT%TZ)" >>"$_runFile"
mv -f "$_runFile" "$START_SIGNAL_FOLDER/${_done_signal_prefix}${RUN_ID}.txt"
"${SCRIPT_HOME:-.}/scripts/teams-notify.sh" fast_view-status --status finished --icon "🏁" --message "Fast-View finished" "${NOTIFY_ARGS[@]}"
debug "Pipeline run $RUN_ID completed."
