#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h"db" -u"myuser" -p"mypassword" --silent; do
    sleep 5
done

echo "MySQL is ready!"

# Run the airlines data import script
echo "Importing airlines data..."
python3 airlines_api_call.py

# Start the Flask app
echo "Starting Flask app..."
python3 user_input.py