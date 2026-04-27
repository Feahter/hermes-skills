#!/bin/bash
# Vercel deployment for web-ppt-skill
# Usage: bash deploy.sh <path-to-html-or-folder>

set -e

TARGET="$1"
if [ -z "$TARGET" ]; then
  echo "Usage: bash deploy.sh <path-to-html-or-folder>"
  exit 1
fi

TARGET=$(realpath "$TARGET")

if [ -f "$TARGET" ]; then
  # Single HTML file — deploy parent directory for image access
  DIR=$(dirname "$TARGET")
  NAME=$(basename "$TARGET" .html)
  echo "Deploying $DIR as '$NAME'..."
  npx vercel deploy "$DIR" --name "$NAME" --yes
elif [ -d "$TARGET" ]; then
  NAME=$(basename "$TARGET")
  echo "Deploying $TARGET as '$NAME'..."
  npx vercel deploy "$TARGET" --name "$NAME" --yes
else
  echo "Error: $TARGET is not a file or directory"
  exit 1
fi
