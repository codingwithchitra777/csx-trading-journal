#!/bin/bash
set -e

# Define cache locations
PREBUILT_CACHE="/app/mpl_cache"
RUNTIME_CACHE="/tmp/mpl_cache"

# Copy pre-built matplotlib cache to writable /tmp
# This prevents Matplotlib from rebuilding the font cache (which takes 1-2 mins)
# because the root filesystem in Cloud Run is read-only.
if [ -d "$PREBUILT_CACHE" ]; then
    echo "Copying Matplotlib cache to $RUNTIME_CACHE..."
    mkdir -p "$RUNTIME_CACHE"
    cp -r "$PREBUILT_CACHE"/* "$RUNTIME_CACHE"/ || true
    export MPLCONFIGDIR="$RUNTIME_CACHE"
fi

# Start the application
exec python main.py
