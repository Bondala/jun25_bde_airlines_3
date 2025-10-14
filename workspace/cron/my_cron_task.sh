#!/bin/bash
echo "Running cron task at $(date)"

# Check if Flask API is ready
if curl -s http://airlines_flask:5000/health > /dev/null; then
    echo "Flask API is ready!"
    # Execute the POST request
    echo "Triggering data import via Flask API..."
    curl -X POST http://airlines_flask:5000/run_data_import
    echo "Cron task finished at $(date)"
else
    echo "Flask API not ready, exiting cron task."
    exit 1
fi
