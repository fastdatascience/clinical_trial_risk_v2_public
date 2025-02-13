#!/bin/bash

celery -b "redis://localhost:6379" -A app.ct_core worker --concurrency=5 -l info &
WORKER_PID=$!

celery -b "redis://localhost:6379" -A app.ct_core beat -l info &
BEAT_PID=$!

function cleanup {
    echo "Stopping Celery worker and beat..."
    kill -9 $WORKER_PID $BEAT_PID
    echo "Both processes stopped."
}

trap cleanup EXIT

wait $WORKER_PID
wait $BEAT_PID
