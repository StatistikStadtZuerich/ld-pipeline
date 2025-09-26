#!/bin/bash

export PYENV_VERSION=3.12.1

if [[ ":$LD_LIBRARY_PATH:" != *":/home/lod_pipeline/openssl_1_1_1/lib:"* ]]; then
  export LD_LIBRARY_PATH="/home/lod_pipeline/openssl_1_1_1/lib:$LD_LIBRARY_PATH"
fi

cd /home/lod_pipeline/ld-pipeline-2024/ || exit 2
/home/lod_pipeline/venv-ld-pipeline-2024/bin/python /home/lod_pipeline/ld-pipeline-2024/run_pipeline_int.py
