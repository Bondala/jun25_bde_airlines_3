#!/bin/bash

echo "Cron setup script started" >> tmp/cron_debug.log

# Wait for Flask/FastAPI app
echo "Waiting for FastAPI app..."
until curl -s http://flask-app:5000/health > /dev/null; do
    echo "FastAPI not ready yet..."
    sleep 5
done
echo "FastAPI is ready!"


echo "Creating cron Job script running inside script."

# Define the cron job line
CRON_JOB="* * * * * curl -X POST http://localhost:5000/run_data_import"

# Check if the job already exists
crontab -l 2>/dev/null | grep -F "$CRON_JOB" >/dev/null

if [ $? -eq 0 ]; then
    echo "Cron job already exists."
else
    # Add the job to the crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added to run every minute."
fi