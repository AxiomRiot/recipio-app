#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVENTS_DIR="$SCRIPT_DIR/../common/events"

echo "Generating typescript json schemas"
npx tsx "$SCRIPT_DIR/../types-ts/scripts/zodToSchemaGenerator.js"

echo "Generating Python Pydantic schemas"
for file in "$EVENTS_DIR"/*.schema.json; do
  [ -e "$file" ] || continue
  filename="$(basename "$file")"
  echo "${filename}"
done
