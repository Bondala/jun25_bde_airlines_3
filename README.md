# Airlines Data Engineering Pipeline

## Overview

This project builds a complete airline data engineering system using Lufthansa API integration with MySQL database backend. The system provides automated data collection, processing, and visualization through Flask API and Streamlit dashboard.

## Features

- Lufthansa API data fetching and processing
- Real-time airport search by coordinates
- Docker containerized deployment
- Cron-based automated scheduling
- MySQL database with connection handling
- Flask REST API endpoints
- System health monitoring

## Project Structure

```
File/Folder                    | Purpose
-------------------------------|-------------------------------------------------------
dockerfile                     | Container build instructions
docker-compose.yml             | Multi-service orchestration setup
init.sql                       | Database schema and seed data
.gitignore                     | Version control exclusions
README.md                      | Project documentation
startup.sh                     | Application startup script
setup_cron.sh                  | Cron job configuration script
workspace/                     | Main application code directory
├── airlines_api_call.py       | API integration and data fetching
├── check_db.py                | Database connection verification
├── get_size.py                | Database monitoring utility
├── manipulate.py              | Data processing functions
├── user_input.py              | Flask API backend
├── templates/index.html       | Web interface
└── cron/                      | Automated task configuration
    ├── Dockerfile             | Cron container build file
    ├── cronjobs               | Cron schedule configuration
    ├── cron.log               | Execution log file
    └── my_cron_task.sh        | Task execution script
```

## Prerequisites

- Docker Engine (version 20.10+)
- Docker Compose (version 2.0+)
- Lufthansa API credentials
- MySQL access

## Quick Setup

### Clone and Configure

```bash
git clone https://github.com/Bondala/jun25_bde_airlines_3.git
cd jun25_bde_airlines_3
```

### Environment Setup

Create `.env` file:

```env
LUFTHANSA_CLIENT_ID=your_client_id
LUFTHANSA_CLIENT_SECRET=your_client_secret

MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=airlines_db
MYSQL_ROOT_PASSWORD=your_root_password

FLASK_ENV=production
FLASK_PORT=5001
```

### Launch Services

```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

### Verify Deployment

```bash
curl http://localhost:5001/health
curl http://localhost:5001/status
```

## API Endpoints

- `GET /` - Web interface
- `GET /health` - System health status
- `GET /status` - Application readiness
- `POST /closest_airport` - Find nearest airport
- `POST /run_data_import` - Trigger data refresh

### Usage Examples

```bash
curl -X POST http://localhost:5001/closest_airport \
  -H "Content-Type: application/json" \
  -d '{"latitude": 48.8566, "longitude": 2.3522}'

curl -X POST http://localhost:5001/run_data_import
```

## Architecture

The system uses microservices approach:

- **API Layer**: Flask endpoints in `workspace/user_input.py`
- **Data Layer**: ETL pipeline via `workspace/airlines_api_call.py`
- **Storage Layer**: MySQL with connection pooling
- **Container Layer**: Docker orchestration
- **Scheduler Layer**: Cron automation in `workspace/cron/`

## Database Schema

Core tables managed through `init.sql`:

- **Airports**: IATA codes, coordinates, location data
- **Airlines**: Carrier information and operational details
- **Routes**: Flight connections and schedules
- **Metadata**: System tracking and logs

## Configuration

### Cron Scheduling

Schedule configured in `workspace/cron/cronjobs`:

```bash
0 3 * * * root /workspace/cron/my_cron_task.sh >> /workspace/cron/cron.log 2>&1
```

### Database Connection

Environment-based connection with retry logic in `workspace/check_db.py`.

## Docker Setup

### Container Build

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    cron curl mysql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x *.sh
RUN chmod +x workspace/cron/*.sh

COPY workspace/cron/cronjobs /etc/cron.d/airlines-cron
RUN chmod 0644 /etc/cron.d/airlines-cron && \
    crontab /etc/cron.d/airlines-cron

EXPOSE 5001
CMD ["./startup.sh"]
```

## Monitoring

### Health Checks

System provides health endpoints through `workspace/user_input.py`:

- Database connectivity status
- API response validation
- Data freshness checks
- Resource utilization metrics

### Logging

```bash
docker-compose logs -f flask-app
docker-compose exec flask-app tail -f /workspace/cron/cron.log
docker-compose logs -f mysql
```

### Backup Operations

```bash
docker-compose exec mysql mysqldump -u root -p airlines_db > backup.sql
docker-compose exec -i mysql mysql -u root -p airlines_db < backup.sql
```

## Testing

### System Validation

```bash
curl -f http://localhost:5001/health || echo "Health check failed"
docker-compose exec flask-app python workspace/check_db.py
docker-compose exec flask-app python workspace/get_size.py
```

## Security

### Environment Protection

Ensure `.env` is gitignored:

```bash
grep -q "\.env" .gitignore && echo "Environment file protected" || echo "Add .env to .gitignore"
```

### API Security

- Input validation on endpoints
- Rate limiting for public access
- CORS configuration for web interface

## Performance

### Database Optimization

- Connection pooling with SQLAlchemy
- Index optimization in `init.sql`
- Batch processing for large datasets

### Caching

- Application-level caching for frequent queries
- Database result caching
- Static asset caching

## Troubleshooting

### Database Connection Issues

```bash
docker-compose ps mysql
docker-compose exec flask-app ping mysql
docker-compose exec flask-app env | grep MYSQL
```

### Cron Job Problems

```bash
docker-compose exec flask-app service cron status
docker-compose exec flask-app crontab -l
docker-compose exec flask-app tail -f /workspace/cron/cron.log
```

### API Response Issues

```bash
docker-compose logs flask-app
docker-compose port flask-app 5001
docker-compose exec flask-app curl localhost:5001/health
```

## Development

### Local Setup

```bash
git clone https://github.com/Bondala/jun25_bde_airlines_3.git
cd jun25_bde_airlines_3

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export FLASK_ENV=development
python workspace/user_input.py
```

### Code Standards

- PEP 8 compliance
- Comprehensive docstrings
- Unit tests for new features
- Documentation updates for API changes

## Deployment Checklist

### Pre-deployment

- Environment variables configured in `.env`
- Database credentials validated
- API keys tested
- Docker images built successfully
- Health checks passing

### Production

- Load balancer configured
- SSL certificates installed
- Monitoring alerts configured
- Backup procedures tested
- Rollback plan documented

## Team

DataScientest Studio - June 2025 BDE Airlines Team 3

Repository: https://github.com/Bondala/jun25_bde_airlines_3

*Updated: October 14, 2025*