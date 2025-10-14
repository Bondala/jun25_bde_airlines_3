FROM python:3.12-slim

# Install cron and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR .

# Copy your scripts
COPY . .

# Copy cron schedule file
COPY cronjobs /etc/cron.d/airlines-cron

# Give execution rights on the cron job file
RUN chmod 0644 /etc/cron.d/airlines-cron

# Apply cron job
RUN crontab /etc/cron.d/airlines-cron

# Keep the container running with cron in foreground
CMD ["cron", "-f"]
