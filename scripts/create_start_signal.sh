#!/usr/bin/env bash

ENV_NAME="${1:-local}"

if [ -z "$SIGNAL_FOLDER" ]; then
  case "$ENV_NAME" in
  prod)
    SIGNAL_FOLDER=/home/lod_pipeline/hdb_dropzone/PROD/Final/Pipeline
    ;;
  int)
    SIGNAL_FOLDER=/home/lod_pipeline/hdb_dropzone/PROD/Test/Pipeline
    ;;
  **)
    SIGNAL_FOLDER=.
    ;;
  esac
fi

SIGNAL="Start_pipeline_$(date '+%F-%H-%M-%S').txt"
echo "Creating Signal '$SIGNAL' in $SIGNAL_FOLDER"
touch "${SIGNAL_FOLDER%/}/$SIGNAL"
