#!/bin/bash -e

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

export PYENV_VERSION=3.12.1
PY_VENV="${PY_VENV:-/home/lod_pipeline/venv-ld-pipeline-2024/}"

if [[ ":$LD_LIBRARY_PATH:" != *":/home/lod_pipeline/openssl_1_1_1/lib:"* ]]; then
  export LD_LIBRARY_PATH="/home/lod_pipeline/openssl_1_1_1/lib:$LD_LIBRARY_PATH"
fi

cd "${SCRIPT_HOME}" || exit 2

ENV="${1:-local}"
ARGS=(--env "$ENV" --config "$SCRIPT_HOME/config.ini")
if [ -f "$SCRIPT_HOME/$ENV.ini" ]; then
  ARGS+=(--config "$SCRIPT_HOME/$ENV.ini")
fi
if [ -f "$SCRIPT_HOME/config-$ENV.ini" ]; then
  ARGS+=(--config "$SCRIPT_HOME/config-$ENV.ini")
fi

"${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_pipeline.py" "${ARGS[@]}"
