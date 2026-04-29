#!/usr/bin/env bash

ENV_NAME="${1:-local}"

CONTENT=""
while [ $# -gt 0 ]; do
    case "$1" in
    --branch)
      CONTENT="${CONTENT}branch=$2\n"
      shift ;;
    --target)
      CONTENT="${CONTENT}target-env=$2\n"
      shift ;;
    esac
    shift
done

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
echo -en "$CONTENT" >"${SIGNAL_FOLDER%/}/$SIGNAL"
