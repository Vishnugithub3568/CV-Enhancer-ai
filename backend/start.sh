#!/usr/bin/env bash
set -e

# Ensure imports resolve even when command is run from repository root.
cd "$(dirname "$0")"

uvicorn app.main:app --host 0.0.0.0 --port 10000
