#!/bin/bash
WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

uwsgi --socket 0.0.0.0:5000 --protocol=http \
    -H ${WORK_DIR}/venv      \
    --chdir ./          \
    --gevent 256        \
    --processes 2       \
    --module app.main   \
    --callable app
