#!/bin/bash

gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 \
    -w 4 \
    --threads 4 \
    --preload \
    --graceful-timeout 300 \
    --timeout 360 \
    --worker-connections 8 \
    --backlog 16 \
    --worker-tmp-dir /dev/shm \
    api:api