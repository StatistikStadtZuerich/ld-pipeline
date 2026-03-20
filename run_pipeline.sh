#!/bin/bash -e

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"
(
  function debug() {
    if [ "$DEBUG" = "true" ]; then
      echo "$(date +"%FT%H:%M:%S%Z") [DEBUG] $*"
    fi
  }
  # Acquire READ-lock on the current directory
  flock -sn 999 || { debug "Could not acquire read-lock"; exit 0; }

  export PYENV_VERSION=3.12.1
  PY_VENV="${PY_VENV:-/home/lod_pipeline/venv-ld-pipeline-2024/}"

  if [[ ":$LD_LIBRARY_PATH:" != *":/home/lod_pipeline/openssl_1_1_1/lib:"* ]]; then
    export LD_LIBRARY_PATH="/home/lod_pipeline/openssl_1_1_1/lib:$LD_LIBRARY_PATH"
  fi

  cd "${SCRIPT_HOME}" || exit 2
  if [ "$GIT_AUTO_UPDATE" == "true" ]; then
    # Acquire WRITE-lock on the current directory
    flock -xn 999 || { debug "Could not acquire write-lock"; exit 0; }

    git pull -q --ff-only || {
      echo "Failed to update git from remote"
      exit 9
    }

    # Re-acquire READ-lock on the current directory
    flock -sn 999 || { debug "Could not acquire read-lock"; exit 0; }
  fi

  ENV="${1:-local}"
  ARGS=(--env "$ENV" --config "$SCRIPT_HOME/config.ini")
  if [ -f "$SCRIPT_HOME/$ENV.ini" ]; then
    ARGS+=(--config "$SCRIPT_HOME/$ENV.ini")
  fi
  if [ -f "$SCRIPT_HOME/config-$ENV.ini" ]; then
    ARGS+=(--config "$SCRIPT_HOME/config-$ENV.ini")
  fi

  "${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_pipeline.py" "${ARGS[@]}"
) 999<"$SCRIPT_HOME"
