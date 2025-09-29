#!/bin/bash
LOG_DIR="/home/lod_pipeline/logs"
DATE_SUFFIX=$(date +%Y%m%d)
LOG_FILE="$LOG_DIR/fuseki_index_int_${DATE_SUFFIX}.log"

/home/lod_pipeline/ld-pipeline-2024/create_fuseki_index_int.sh >> "$LOG_FILE" 2>&1
