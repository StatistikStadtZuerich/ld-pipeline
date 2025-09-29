#!/bin/bash

SCRIPT="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SCRIPT")"

export PYENV_VERSION=3.12.1
PY_VENV="${PY_VENV:-/home/lod_pipeline/venv-ld-pipeline-2024/}"

if [[ ":$LD_LIBRARY_PATH:" != *":/home/lod_pipeline/openssl_1_1_1/lib:"* ]]; then
  export LD_LIBRARY_PATH="/home/lod_pipeline/openssl_1_1_1/lib:$LD_LIBRARY_PATH"
fi

cd "${SCRIPT_HOME}" || exit 2
"${PY_VENV%/}/bin/python" "${SCRIPT_HOME}/run_pipeline.py" --env "int"
