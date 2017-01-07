#!/bin/bash
WORK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo ${WORK_DIR}
PYTHONPATH=${WORK_DIR} python -m app.main
