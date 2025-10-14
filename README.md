# Airlines Data Engineering Pipeline

## Overview
A comprehensive airline data engineering pipeline that integrates with the Lufthansa API to fetch, process, and store aviation data in a MySQL database. This project includes automated scheduling, containerized deployment with Docker, and a Flask API for real-time data queries.

## 🚀 Features
- **Lufthansa API Integration**: Automated data fetching from official airline APIs
- **Real-time Airport Search**: Find closest airports by geographical coordinates
- **Containerized Deployment**: Complete Docker-based solution
- **Automated Scheduling**: Cron-based periodic data updates
- **Database Management**: MySQL with connection pooling and retry logic
- **RESTful API**: Flask-based endpoints for data access
- **Health Monitoring**: Built-in health checks and status endpoints

## 📁 Project Structure
```
File/Folder                 |  Description                                          
----------------------------+-------------------------------------------------------
Dockerfile                  |  Image instructions for building the Python/Flask app.
docker-compose.yml          |  Orchestrates multi-container deployment (app + DB).  
init.sql                    |  MySQL schema and initial data load for airports.     
user_input.py               |  Main Flask API backend for requests and processing.  
index.html/index-Copy.html  |  Web interface for map and airport lookup.            
startup.sh                  |  Application startup script.                          
setup_cron.sh               |  Script to create and manage cron jobs for automation.
my_cron_task.sh             |  Cron job script that triggers FastAPI data import.   
get_size.py,manipulate.py   |  Utility scripts for DB checks and manipulation.      
cronjobs                    |  Contains crontab entries.                            
workspace/                  |  Directory for persistent/local files (if used).      
```

## 🛠️ Prerequisites
- Docker Engine (≥20.10)
- Docker Compose (≥2.0)
- Lufthansa API credentials
- MySQL server access

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/DataScientest-Studio/jun25_bde_airlines_3.git
cd jun25_bde_airlines_3
```

### 2. Environment Configuration
Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```dotenv
# Lufthansa API Configuration
LUFTHANSA_CLIENT_ID=your_client_id_here
LUFTHANSA_CLIENT_SECRET=your_client_secret_here

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=airlines_db

# Application Configuration
FLASK_ENV=production
FLASK_PORT=5001
```

### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs -f
```

### 4. Health Check
```bash
# API health check
curl http://localhost:5001/health

# Database status
curl http://localhost:5001/status
```

## 📊 API Endpoints

### Core Endpoints
- `GET /` - Web interface
- `GET /health` - System health status
- `GET /status` - Application readiness
- `POST /closest_airport` - Find nearest airport
- `POST /run_data_import` - Trigger data refresh

### Usage Examples
```bash
# Find closest airport
curl -X POST http://localhost:5001/closest_airport \
  -H "Content-Type: application/json" \
  -d '{"latitude": 48.8566, "longitude": 2.3522}'

# Manual data import
curl -X POST http://localhost:5001/run_data_import
```

## 🏗️ Architecture
<img width="584" height="734" alt="image" src="https://github.com/user-attachments/assets/3a10d107-681c-4107-9c74-f98eb91c3c01" />

### System Architecture
![Architecture Diagram](docs/architecture/system_architecture.png)

The system follows a microservices architecture with:
- **API Layer**: Flask-based REST endpoints
- **Processing Layer**: ETL pipeline with data transformation
- **Storage Layer**: MySQL database with connection pooling
- **Orchestration Layer**: Docker containers with automated scheduling

### Database Schema
![Database ER Diagram](docs/architecture/database_schema.png)

Core entities:
- **Airports**: IATA codes, coordinates, country information
- **Airlines**: Carrier details and operational data
- **Routes**: Flight connections and scheduling
- **Metadata**: System tracking and audit logs
<img width="975" height="487" alt="image" src="https://github.com/user-attachments/assets/dee3e2e4-c59f-4747-a0ae-d9071c7cae06" />

## 🔧 Configuration

### Cron Scheduling
Default schedule (modify in `config/cronjobs`):
```cron
# Production: Daily at 3 AM
0 3 * * * root /workspace/scripts/my_cron_task.sh >> /var/log/cron.log 2>&1

# Development: Every minute
* * * * * root /workspace/scripts/my_cron_task.sh >> /var/log/cron.log 2>&1
```

### Database Connection
Connection string format:
```python
mysql+pymysql://username:password@host:port/database
```

Features:
- Connection pooling with pre-ping validation
- Automatic reconnection on failure
- Configurable retry logic

## 🐳 Docker Configuration

### Multi-stage Build
```dockerfile
FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    cron curl mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Application setup
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Set permissions
RUN chmod +x scripts/*.sh

# Configure cron
COPY config/cronjobs /etc/cron.d/airlines-cron
RUN chmod 0644 /etc/cron.d/airlines-cron && \
    crontab /etc/cron.d/airlines-cron

EXPOSE 5001
CMD ["./scripts/startup.sh"]
```

## 🚨 Monitoring & Maintenance

### Health Monitoring
The system provides comprehensive health endpoints:
- Database connectivity status
- API responsiveness checks
- Data freshness validation
- Resource utilization metrics

### Logging
Centralized logging with rotation:
```bash
# View application logs
docker-compose logs -f flask-app

# Monitor cron execution
docker-compose exec flask-app tail -f /var/log/cron.log

# Database operation logs
docker-compose logs -f mysql
```

### Backup & Recovery
```bash
# Database backup
docker-compose exec mysql mysqldump -u root -p airlines_db > backup.sql

# Restore from backup
docker-compose exec -i mysql mysql -u root -p airlines_db < backup.sql
```

## 🧪 Testing

### Unit Tests
```bash
# Run test suite
docker-compose exec flask-app python -m pytest tests/

# Coverage report
docker-compose exec flask-app python -m pytest --cov=src tests/
```

### Integration Tests
```bash
# API endpoint tests
curl -f http://localhost:5001/health || echo "Health check failed"

# Database connectivity
docker-compose exec flask-app python src/check_db.py
```

## 🔒 Security

### Environment Variables
Never commit sensitive data. Use Docker secrets in production:
```yaml
services:
  flask-app:
    secrets:
      - mysql_password
      - api_credentials
```

### API Security
- Input validation on all endpoints
- Rate limiting for public endpoints
- CORS configuration for web interface

## 📈 Performance Optimization

### Database Optimization
- Connection pooling with SQLAlchemy
- Query optimization with indexes
- Batch processing for large datasets

### Caching Strategy
- Application-level caching for frequent queries
- Database query result caching
- Static asset caching

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check MySQL container status
docker-compose ps mysql

# Verify network connectivity
docker-compose exec flask-app ping mysql

# Review connection credentials
docker-compose exec flask-app env | grep MYSQL
```

**Cron Jobs Not Running**
```bash
# Check cron service status
docker-compose exec flask-app service cron status

# Verify cron configuration
docker-compose exec flask-app crontab -l

# Review cron logs
docker-compose exec flask-app tail -f /var/log/cron.log
```

**API Endpoints Unresponsive**
```bash
# Check Flask application logs
docker-compose logs flask-app

# Verify port binding
docker-compose port flask-app 5001

# Test internal connectivity
docker-compose exec flask-app curl localhost:5001/health
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/DataScientest-Studio/jun25_bde_airlines_3.git
cd jun25_bde_airlines_3

# Create development environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
export FLASK_ENV=development
python src/user_input.py
```

### Code Standards
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Add unit tests for new features
- Update documentation for API changes

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] Database credentials validated
- [ ] API keys tested
- [ ] Docker images built successfully
- [ ] Health checks passing

### Production Deployment
- [ ] Load balancer configured
- [ ] SSL certificates installed
- [ ] Monitoring alerts configured
- [ ] Backup procedures tested
- [ ] Rollback plan documented

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team
**DataScientest Studio - June 2025 BDE Airlines Team 3**

For questions or support, please create an issue in the GitHub repository.

---
*Last updated: September 30, 2025*
