#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_FILE="${ROOT_DIR}/bof-index.json"
TARGET_FILE="${ROOT_DIR}/site/data/bof-index.json"

if [[ ! -f "${SOURCE_FILE}" ]]; then
  echo "Error: ${SOURCE_FILE} not found" >&2
  exit 1
fi

mkdir -p "$(dirname "${TARGET_FILE}")"
cp "${SOURCE_FILE}" "${TARGET_FILE}"

echo "Synced bof-index.json -> site/data/bof-index.json"
