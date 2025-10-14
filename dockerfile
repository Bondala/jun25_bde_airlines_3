# Base image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and ensure python points to python3
RUN apt-get update && \
    apt-get install -y \
      python3 python3-pip cron curl \
      default-libmysqlclient-dev build-essential \
      libssl-dev libffi-dev mysql-client && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make all shell scripts executable
RUN find . -type f -name "*.sh" -exec chmod +x {} +

# Configure cron jobs
COPY workspace/cron/cronjobs /etc/cron.d/airlines-cron
RUN chmod 0644 /etc/cron.d/airlines-cron && \
    crontab /etc/cron.d/airlines-cron

EXPOSE 5001

# Start cron and then the Flask app
CMD ["bash", "-c", "service cron start && ./startup.sh"]

