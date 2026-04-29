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
loadSetting() {
  # $1 setting
  # $2 fallback
  # $3 input
  local value
  value=$(grep -i "^$1[:=]" "$3" | sed -r 's/^[^:=]+[:=]//; s/ //g' | head -1)
  if [ -z "${value:-}" ]; then
    echo "$2"
  else
    echo "$value"
  fi
}
##############################################
ENV="${1:-local}"

# Determine default settings
case "$ENV" in
  prod)
    branch=main
    ;;
  *)
    branch=develop
    ;;
esac

runningSignal="$(findRunningSignal)"
[ -z "$runningSignal" ] || { debug "Detected running pipeline: '$runningSignal'; STOP"; exit 0; }

startSignal="$(findStartSignal)"
[ -z "$startSignal" ] && { debug "No start-signal found in '$(readlink -f "$START_SIGNAL_FOLDER")'"; exit 0; }
[ -r "$startSignal" ] || { debug "Could not read start-signal '$startSignal'"; exit 1; }
# Extract the run-id
RUN_ID="$(basename "$startSignal" .txt | sed "s/$_start_signal_prefix//")"
# Extract further run-parameters for the pipeline
branch="$(loadSetting branch "$branch" "$startSignal")"
target_env="$(loadSetting target-env "$ENV" "$startSignal")"
( # Lock the start-signal for execution
  flock -xn 1001 || { debug "Could not acquire exclusive lock on '$startSignal'"; exit 0; }
  debug "Starting ($ENV) Pipeline with runID $RUN_ID"

  # Create Running-Signal
  _runFile="$START_SIGNAL_FOLDER/${_running_signal_prefix}${RUN_ID}.txt"
  cat >"$_runFile" <<EOF
Started: $(date -u +%FT%TZ)
  Run ID: $RUN_ID
  Env: $ENV
  Branch: $branch
  Target-Env: $target_env
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

    (git fetch -qf && git checkout -qf "$branch") || {
      echo "Failed to update git from remote"
      exit 9
    }

    # Re-acquire READ-lock on the current directory
    flock -sn 999 || { debug "Could not acquire read-lock"; exit 0; }
  fi

  ARGS=(
    --env "$ENV"
    --runId "$RUN_ID"
    --targetEnv "$target_env"
    --config "$SCRIPT_HOME/config.ini"
  )
  if [ -f "$SCRIPT_HOME/$ENV.ini" ]; then
    ARGS+=(--config "$SCRIPT_HOME/$ENV.ini")
  fi
  if [ -f "$SCRIPT_HOME/config-$ENV.ini" ]; then
    ARGS+=(--config "$SCRIPT_HOME/config-$ENV.ini")
  fi

  NOTIFY_ARGS=(
    --environment "$(echo "$ENV" | tr '[:lower:]' '[:upper:]')"
    --runId "$RUN_ID"
    --branch "$branch"
    --targetEnv "$(echo "$target_env" | tr '[:lower:]' '[:upper:]')"
  )
  "${SCRIPT_HOME:-.}/scripts/teams-notify.sh" pipeline-status --status started --icon "🚀" "${NOTIFY_ARGS[@]}"
  "${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_pipeline.py" "${ARGS[@]}"

  echo "Completed: $(date -u +%FT%TZ)" >>"$_runFile"
  mv -f "$_runFile" "$(dirname "$_runFile")/$(basename "$_runFile" | sed "s/^$_running_signal_prefix/$_done_signal_prefix/")"
  "${SCRIPT_HOME:-.}/scripts/teams-notify.sh" pipeline-status --status finished --icon "🏁" "${NOTIFY_ARGS[@]}"
  debug "Pipeline run $RUN_ID completed."
) 999<"$SCRIPT_HOME" 1001<>"$startSignal"
