#!/bin/bash
WORK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo ${WORK_DIR}
source ${WORK_DIR}/venv/bin/activate
PYTHONPATH=${WORK_DIR} python -m app.main


