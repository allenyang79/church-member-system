#!/bin/bash
WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

source ${WORK_DIR}/venv/bin/activate
uwsgi --socket 0.0.0.0:5000 --protocol=http \
    --chdir ${WORK_DIR}                     \
    --check-static ${WORK_DIR}/static       \
    --static-map /static=${WORK_DIR}/static \
    --gevent 256        \
    --processes 4       \
    --module app.main   \
    --callable app
