#!/bin/bash

DONE_DIR="/home/lod_pipeline/ld-pipeline-2024/output/int/done/"
FUSEKI_INDEX_DIR="/home/lod_pipeline/ld-pipeline-2024/fuseki_index/int/"
PIPELINE_DATA_DIR="/home/lod_pipeline/hdb_dropzone/prod/test/pipeline_data"

# 1) Lösche alle regulären Dateien im Ordner $DONE_DIR, die älter als 24 h sind
find "$DONE_DIR" -type f -mmin +1440 -delete

# 2) Lösche in $FUSEKI_INDEX_DIR nur Dateien/Ordner,
#    die älter als 1 Tag sind, aber nicht den Symlink "current"
#    und nicht dessen Zielverzeichnis.

SYMLINK_PATH="$FUSEKI_INDEX_DIR/current"
if [ -L "$SYMLINK_PATH" ]; then
    TARGET_DIR=$(readlink -f "$SYMLINK_PATH")
else
    TARGET_DIR=""
fi

for ITEM in "$FUSEKI_INDEX_DIR"/*; do
    # Überspringen, wenn es sich um den Symlink oder sein Zielverzeichnis handelt
    if [ "$ITEM" = "$SYMLINK_PATH" ] || [ "$ITEM" = "$TARGET_DIR" ]; then
        continue
    fi

    if find "$ITEM" -prune -mmin +1440 | grep -q .; then
        rm -rf "$ITEM"
    fi
done

# 3) Lösche alle *.tar.gz Dateien in $PIPELINE_DATA_DIR, die älter als 30 Tage sind
find "$PIPELINE_DATA_DIR" -type f -name "*.tar.gz" -mtime +30 -delete

