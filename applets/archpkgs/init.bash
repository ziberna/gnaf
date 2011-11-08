#!/bin/bash
# Init script
echo "start"

if [ "$1" == "" ] || [ "$2" == "" ] || [ "$3" == "" ]; then
    echo "Error: missing variables ($1, $2, $3)"
    exit 0
fi

TMP_DIR="$1"
LCL_DIR="$2/$3"
TMP_DIR_SL="$1/$3"

# Check if the dir exists
if [ ! -d "$TMP_DIR" ]; then
    mkdir "$TMP_DIR"
fi

# Check if dir with symlink exists
if [ -d "$TMP_DIR_SL" ]; then
    if [ ! -L "$TMP_DIR_SL" ]; then
        rmdir "$TMP_DIR_SL"
        ln -s "$LCL_DIR" "$TMP_DIR"
    fi
else
    ln -s "$LCL_DIR" "$TMP_DIR"    
fi

if [ -f "$TMP_DIR/db.lck" ]; then
    rm -f "$TMP_DIR/db.lck"
fi

echo "success"
exit 0
