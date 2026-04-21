#!/bin/bash
set -euo pipefail

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"
START_SIGNAL_FOLDER="${START_SIGNAL_FOLDER:-.}"
##############################################
_start_signal_prefix="Start_pipeline_"
_running_signal_prefix="Running_pipeline_"
_done_signal_prefix="Finished_pipeline_"
##############################################
debug() {
  if [ "${DEBUG:-false}" = "true" ]; then
    echo "$(date -u +%FT%TZ) [DEBUG] $*"
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
##############################################
ENV="${1:-local}"

runningSignal="$(findRunningSignal)"
[ -z "$runningSignal" ] || { debug "Detected running pipeline: '$runningSignal'; STOP"; exit 0; }

startSignal="$(findStartSignal)"
[ -z "$startSignal" ] && { debug "No start-signal found in '$(readlink -f "$START_SIGNAL_FOLDER")'"; exit 0; }
[ -r "$startSignal" ] || { debug "Could not read start-signal '$startSignal'"; exit 1; }
# Extract the run-id
RUN_ID="$(basename "$startSignal" .txt | sed "s/$_start_signal_prefix//")"
( # Lock the start-signal for execution
  flock -xn 1001 || { debug "Could not acquire exclusive lock on '$startSignal'"; exit 0; }
  debug "Starting ($ENV) Pipeline with runID $RUN_ID"
  # TODO(future work): Read settings from the start-signal

  # Create Running-Signal
  _runFile="$START_SIGNAL_FOLDER/${_running_signal_prefix}${RUN_ID}.txt"
  cat >"$_runFile" <<EOF
Started: $(date -u +%FT%TZ)
  Run ID: $RUN_ID
  Env: $ENV
EOF
  # Move start-signal out of the way
  mkdir -p "$START_SIGNAL_FOLDER/done"
  mv "$startSignal" "$START_SIGNAL_FOLDER/done/"
  echo "Started: $(date -u +%FT%TZ)" >&1001

  # Launch the Pipeline-Execution
  # Acquire READ-lock on the current directory
  flock -sn 999 || { debug "Could not acquire read-lock"; exit 0; }

  export PYENV_VERSION=3.12.1
  PY_VENV="${PY_VENV:-/home/lod_pipeline/venv-ld-pipeline-2024/}"

  if [ -n "${LD_LIBRARY_PATH:-}" ] && [[ ":$LD_LIBRARY_PATH:" != *":/home/lod_pipeline/openssl_1_1_1/lib:"* ]]; then
    export LD_LIBRARY_PATH="/home/lod_pipeline/openssl_1_1_1/lib:$LD_LIBRARY_PATH"
  fi

  cd "${SCRIPT_HOME}" || exit 2
  if [ "${GIT_AUTO_UPDATE:-false}" == "true" ]; then
    # Acquire WRITE-lock on the current directory
    flock -xn 999 || { debug "Could not acquire write-lock"; exit 0; }

    git pull -q --ff-only || {
      echo "Failed to update git from remote"
      exit 9
    }

    # Re-acquire READ-lock on the current directory
    flock -sn 999 || { debug "Could not acquire read-lock"; exit 0; }
  fi

  ARGS=(
    --env "$ENV"
    --runId "$RUN_ID"
    --config "$SCRIPT_HOME/config.ini"
  )
  if [ -f "$SCRIPT_HOME/$ENV.ini" ]; then
    ARGS+=(--config "$SCRIPT_HOME/$ENV.ini")
  fi
  if [ -f "$SCRIPT_HOME/config-$ENV.ini" ]; then
    ARGS+=(--config "$SCRIPT_HOME/config-$ENV.ini")
  fi

  "${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_pipeline.py" "${ARGS[@]}"

  echo "Completed: $(date -u +%FT%TZ)" >>"$_runFile"
  mv -f "$_runFile" "$(dirname "$_runFile")/$(basename "$_runFile" | sed "s/^$_running_signal_prefix/$_done_signal_prefix/")"
  debug "Pipeline run $RUN_ID completed."
) 999<"$SCRIPT_HOME" 1001<>"$startSignal"
