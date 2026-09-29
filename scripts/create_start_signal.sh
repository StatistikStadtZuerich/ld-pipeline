#!/usr/bin/env bash

ENV_NAME=""
CONTENT=""
VIEW_IDS=""
while [ $# -gt 0 ]; do
    case "$1" in
    --view)
      # Repeatable; a comma separated list in a single --view works as well.
      [ -n "${2:-}" ] || { echo "--view needs a value" >&2; exit 1; }
      VIEW_IDS="${VIEW_IDS:+$VIEW_IDS,}$2"
      shift ;;
    --branch)
      CONTENT="${CONTENT}branch=$2\n"
      shift ;;
    --target)
      CONTENT="${CONTENT}target-env=$2\n"
      shift ;;
    -*)
      echo "Unknown parameter '$1'" >&2
      exit 1 ;;
    *)
      if [ -n "$ENV_NAME" ]; then
        echo "Env already set to '$ENV_NAME', ignoring '$1'" >&2
        exit 1
      fi
      ENV_NAME="$1" ;;
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
  dev)
    SIGNAL_FOLDER=/home/lod_pipeline/hdb_dropzone/DEV/Pipeline
    ;;
  **)
    SIGNAL_FOLDER=.
    ;;
  esac
fi

# With view-ids this becomes a fast-view signal. That one carries nothing but the
# ids - branch and target-env have no meaning for it.
if [ -n "$VIEW_IDS" ]; then
  [ -z "$CONTENT" ] || echo "Ignoring --branch/--target, a fast-view signal only carries view-ids" >&2
  SIGNAL_PREFIX="Start_fastview_"
  CONTENT="$VIEW_IDS"
else
  SIGNAL_PREFIX="Start_pipeline_"
fi

SIGNAL="${SIGNAL_PREFIX}$(date '+%F-%H-%M-%S').txt"
echo "Creating Signal '$SIGNAL' in $SIGNAL_FOLDER"
mkdir -p "$SIGNAL_FOLDER"
echo -en "$CONTENT" >"${SIGNAL_FOLDER%/}/$SIGNAL"
