# Deployment Guide
## Emotion-Aware Multi-Factor Authentication System

---

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [Local Deployment](#local-deployment)
3. [Cloud Deployment (Heroku)](#cloud-deployment-heroku)
4. [Cloud Deployment (AWS)](#cloud-deployment-aws)
5. [Cloud Deployment (Azure)](#cloud-deployment-azure)
6. [Docker Deployment](#docker-deployment)
7. [Production Checklist](#production-checklist)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Deployment Options

### 1. **Local/Development** (Current Setup)
- Best for: Testing, development, demos
- Cost: Free
- Complexity: Low
- Scalability: Limited

### 2. **Cloud Platform (PaaS)**
- Best for: Production, scalability
- Cost: $7-50/month
- Complexity: Medium
- Scalability: High
- Options: Heroku, Railway, Render

### 3. **Cloud Infrastructure (IaaS)**
- Best for: Enterprise, custom requirements
- Cost: $10-100+/month
- Complexity: High
- Scalability: Very High
- Options: AWS, Azure, Google Cloud

### 4. **Docker Container**
- Best for: Consistent deployment, microservices
- Cost: Varies by platform
- Complexity: Medium
- Scalability: High

---

## Local Deployment

### Current Setup (Already Working)

**Start Server:**
```bash
# Windows
start_server.bat

# Linux/Mac
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Access:**
- Authentication: http://localhost:8000/web/index.html
- Admin: http://localhost:8000/web/admin.html
- API Docs: http://localhost:8000/docs

**Make Accessible on Local Network:**
```bash
# Find your local IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# Start server on all interfaces
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Access from other devices
http://YOUR_LOCAL_IP:8000/web/index.html
```

**Note:** Camera/microphone require HTTPS or localhost for security.

---

## Cloud Deployment (Heroku)

### Prerequisites
- Heroku account (free tier available)
- Git installed
- Heroku CLI installed

### Step 1: Install Heroku CLI
```bash
# Windows (using Chocolatey)
choco install heroku-cli

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Prepare Project Files

**Create Procfile:**
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Create runtime.txt:**
```
python-3.10.12
```

**Update requirements.txt** (add gunicorn):
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
sqlalchemy==2.0.23
pydantic==2.5.0
numpy==1.24.3
opencv-python-headless==4.8.1.78
tensorflow==2.14.0
scikit-learn==1.3.2
pandas==2.1.3
python-multipart==0.0.6
```

### Step 3: Deploy to Heroku
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Add buildpacks
heroku buildpacks:add --index 1 heroku/python

# Deploy
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# Open app
heroku open
```

### Step 4: Configure Environment
```bash
# Set environment variables
heroku config:set DATABASE_URL=sqlite:///./backend/storage/auth.db

# View logs
heroku logs --tail
```

**Important:** Heroku uses ephemeral filesystem. For production, use PostgreSQL:
```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Update DATABASE_URL in code to use PostgreSQL
```

---

## Cloud Deployment (AWS)

### Option 1: AWS Elastic Beanstalk (Easiest)

**Prerequisites:**
- AWS account
- AWS CLI installed
- EB CLI installed

**Step 1: Install EB CLI**
```bash
pip install awsebcli
```

**Step 2: Initialize EB**
```bash
eb init -p python-3.10 emotion-auth-system

# Select region
# Create new application
```

**Step 3: Create Environment**
```bash
eb create emotion-auth-env

# Wait for deployment (5-10 minutes)
```

**Step 4: Deploy Updates**
```bash
eb deploy
```

**Step 5: Open Application**
```bash
eb open
```

### Option 2: AWS EC2 (More Control)

**Step 1: Launch EC2 Instance**
- AMI: Ubuntu 22.04 LTS
- Instance Type: t2.medium (2 vCPU, 4GB RAM)
- Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

**Step 2: Connect and Setup**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.10 python3-pip nginx -y

# Clone repository
git clone your-repo-url
cd emotion_auth_system

# Install dependencies
pip3 install -r requirements.txt
```

**Step 3: Setup Nginx**
```bash
sudo nano /etc/nginx/sites-available/emotion-auth
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/emotion-auth /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Step 4: Setup Systemd Service**
```bash
sudo nano /etc/systemd/system/emotion-auth.service
```

```ini
[Unit]
Description=Emotion Auth System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/emotion_auth_system
ExecStart=/usr/local/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl enable emotion-auth
sudo systemctl start emotion-auth
sudo systemctl status emotion-auth
```

**Step 5: Setup SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```



---

## Cloud Deployment (Azure)

### Azure App Service

**Step 1: Install Azure CLI**
```bash
# Windows
winget install Microsoft.AzureCLI

# Or download from: https://aka.ms/installazurecliwindows
```

**Step 2: Login and Create Resources**
```bash
# Login
az login

# Create resource group
az group create --name emotion-auth-rg --location eastus

# Create App Service plan
az appservice plan create --name emotion-auth-plan --resource-group emotion-auth-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group emotion-auth-rg --plan emotion-auth-plan --name your-app-name --runtime "PYTHON:3.10"
```

**Step 3: Configure Deployment**
```bash
# Configure deployment from local Git
az webapp deployment source config-local-git --name your-app-name --resource-group emotion-auth-rg

# Get deployment credentials
az webapp deployment list-publishing-credentials --name your-app-name --resource-group emotion-auth-rg
```

**Step 4: Deploy**
```bash
# Add Azure remote
git remote add azure <deployment-url>

# Push to Azure
git push azure main
```

**Step 5: Configure Startup Command**
```bash
az webapp config set --resource-group emotion-auth-rg --name your-app-name --startup-file "uvicorn backend.main:app --host 0.0.0.0 --port 8000"
```

---

## Docker Deployment

### Step 1: Create Dockerfile

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create storage directories
RUN mkdir -p backend/storage/trained_models \
    backend/storage/kd_models \
    backend/storage/alerts \
    backend/storage/datasets

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create docker-compose.yml

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./backend/storage:/app/backend/storage
    environment:
      - DATABASE_URL=sqlite:///./backend/storage/auth.db
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add PostgreSQL for production
  # db:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: emotion_auth
  #     POSTGRES_USER: admin
  #     POSTGRES_PASSWORD: your_password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   restart: unless-stopped

# volumes:
#   postgres_data:
```

### Step 3: Create .dockerignore

**.dockerignore:**
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.git/
.gitignore
.vscode/
.idea/
*.md
!README.md
.env
*.log
```

### Step 4: Build and Run

```bash
# Build image
docker build -t emotion-auth-system .

# Run container
docker run -d -p 8000:8000 --name emotion-auth emotion-auth-system

# Or use docker-compose
docker-compose up -d

# View logs
docker logs -f emotion-auth

# Stop container
docker stop emotion-auth

# Remove container
docker rm emotion-auth
```

### Step 5: Deploy to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag emotion-auth-system your-username/emotion-auth-system:latest

# Push to Docker Hub
docker push your-username/emotion-auth-system:latest

# Pull and run on any server
docker pull your-username/emotion-auth-system:latest
docker run -d -p 8000:8000 your-username/emotion-auth-system:latest
```

---

## Production Checklist

### Security

- [ ] **Enable HTTPS/TLS**
  - Use Let's Encrypt for free SSL certificates
  - Configure Nginx/Apache as reverse proxy

- [ ] **Hash Passphrases**
  ```python
  from passlib.hash import bcrypt
  hashed = bcrypt.hash(passphrase)
  bcrypt.verify(passphrase, hashed)
  ```

- [ ] **Add Rate Limiting**
  ```python
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)
  
  @app.post("/api/auth/attempt")
  @limiter.limit("5/minute")
  async def auth_attempt(...):
  ```

- [ ] **Implement CORS Restrictions**
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://yourdomain.com"],
      allow_credentials=True,
      allow_methods=["POST", "GET"],
      allow_headers=["*"],
  )
  ```

- [ ] **Add Authentication for Admin Endpoints**
  ```python
  from fastapi.security import HTTPBasic, HTTPBasicCredentials
  security = HTTPBasic()
  
  @app.get("/api/admin/logs")
  async def admin_logs(credentials: HTTPBasicCredentials = Depends(security)):
      # Verify credentials
  ```

- [ ] **Environment Variables for Secrets**
  ```python
  import os
  SECRET_KEY = os.getenv("SECRET_KEY")
  DATABASE_URL = os.getenv("DATABASE_URL")
  ```

- [ ] **Input Validation & Sanitization**
  - Already using Pydantic models ✓
  - Add additional validation as needed

- [ ] **SQL Injection Prevention**
  - Already using SQLAlchemy ORM ✓
  - Avoid raw SQL queries

### Performance

- [ ] **Use PostgreSQL Instead of SQLite**
  ```python
  # Install: pip install psycopg2-binary
  DATABASE_URL = "postgresql://user:password@localhost/dbname"
  ```

- [ ] **Enable Caching**
  ```python
  from functools import lru_cache
  
  @lru_cache(maxsize=100)
  def load_model():
      return keras.models.load_model(MODEL_PATH)
  ```

- [ ] **Optimize Image Sizes**
  - Already using JPEG compression ✓
  - Already resizing to 50% ✓

- [ ] **Add Request Queuing**
  ```python
  from fastapi_limiter import FastAPILimiter
  ```

- [ ] **Use CDN for Static Files**
  - CloudFlare, AWS CloudFront, Azure CDN

- [ ] **Enable Gzip Compression**
  ```python
  from fastapi.middleware.gzip import GZipMiddleware
  app.add_middleware(GZipMiddleware, minimum_size=1000)
  ```

### Monitoring

- [ ] **Setup Logging**
  ```python
  import logging
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      handlers=[
          logging.FileHandler('app.log'),
          logging.StreamHandler()
      ]
  )
  ```

- [ ] **Add Health Check Endpoint**
  ```python
  @app.get("/health")
  async def health_check():
      return {"status": "healthy", "timestamp": datetime.now()}
  ```

- [ ] **Monitor Error Rates**
  - Use Sentry, Rollbar, or similar

- [ ] **Track Performance Metrics**
  - Response times, CPU usage, memory

- [ ] **Setup Alerts**
  - Email/SMS for critical errors
  - Slack/Discord webhooks

### Database

- [ ] **Regular Backups**
  ```bash
  # SQLite backup
  sqlite3 auth.db ".backup backup.db"
  
  # PostgreSQL backup
  pg_dump dbname > backup.sql
  ```

- [ ] **Database Migrations**
  ```bash
  # Install Alembic
  pip install alembic
  
  # Initialize
  alembic init alembic
  
  # Create migration
  alembic revision --autogenerate -m "description"
  
  # Apply migration
  alembic upgrade head
  ```

- [ ] **Connection Pooling**
  ```python
  engine = create_engine(
      DATABASE_URL,
      pool_size=10,
      max_overflow=20
  )
  ```



---

## Monitoring & Maintenance

### Application Monitoring

**Setup Prometheus + Grafana:**
```bash
# Install Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Install Grafana
docker run -d -p 3000:3000 grafana/grafana
```

**Add Metrics to FastAPI:**
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### Log Management

**Centralized Logging:**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'app.log',
    maxBytes=10000000,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

### Automated Backups

**Backup Script (backup.sh):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
sqlite3 backend/storage/auth.db ".backup $BACKUP_DIR/auth_$DATE.db"

# Backup models
tar -czf $BACKUP_DIR/models_$DATE.tar.gz backend/storage/trained_models/

# Backup alerts
tar -czf $BACKUP_DIR/alerts_$DATE.tar.gz backend/storage/alerts/

# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Setup Cron Job:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

### Update Strategy

**Zero-Downtime Deployment:**
```bash
# Using Docker
docker-compose pull
docker-compose up -d --no-deps --build app

# Using systemd
sudo systemctl reload emotion-auth
```

**Rollback Plan:**
```bash
# Keep previous version
docker tag emotion-auth-system:latest emotion-auth-system:backup

# Rollback if needed
docker stop emotion-auth
docker run -d -p 8000:8000 emotion-auth-system:backup
```

---

## Quick Deployment Commands

### Heroku (Fastest)
```bash
heroku create your-app-name
git push heroku main
heroku open
```

### Docker (Most Portable)
```bash
docker build -t emotion-auth .
docker run -d -p 8000:8000 emotion-auth
```

### AWS EC2 (Most Control)
```bash
# On EC2 instance
git clone your-repo
cd emotion_auth_system
pip3 install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## Troubleshooting Deployment

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Kill process
taskkill /PID <pid> /F        # Windows
kill -9 <pid>                 # Linux/Mac
```

**2. Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**3. Database Locked**
```bash
# Stop all processes
# Delete database
rm backend/storage/auth.db
# Restart server (will recreate)
```

**4. Camera/Microphone Not Working**
- Ensure HTTPS is enabled
- Check browser permissions
- Verify SSL certificate is valid

**5. High Memory Usage**
```bash
# Reduce model size
# Use CPU-only TensorFlow
pip install tensorflow-cpu

# Limit workers
uvicorn backend.main:app --workers 1
```

---

## Cost Estimates

### Free Tier Options
- **Heroku**: Free (with limitations)
- **Railway**: $5/month free credit
- **Render**: Free tier available
- **AWS**: 12 months free tier
- **Azure**: $200 free credit

### Paid Options
- **Heroku Hobby**: $7/month
- **AWS t2.medium**: ~$30/month
- **Azure B1**: ~$13/month
- **DigitalOcean Droplet**: $12/month

### Recommended for Production
- **Small Scale** (<100 users): Heroku Hobby ($7/month)
- **Medium Scale** (100-1000 users): AWS t2.medium ($30/month)
- **Large Scale** (1000+ users): AWS t2.large + RDS ($100+/month)

---

## Support & Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Docker: https://docs.docker.com/
- Heroku: https://devcenter.heroku.com/
- AWS: https://docs.aws.amazon.com/

### Community
- Stack Overflow
- GitHub Issues
- FastAPI Discord
- Reddit r/FastAPI

---

## Next Steps

1. **Choose Deployment Platform** based on your needs
2. **Follow Platform-Specific Guide** above
3. **Complete Production Checklist** for security
4. **Setup Monitoring** for reliability
5. **Test Thoroughly** before going live
6. **Document Your Setup** for team reference

---

**Deployment Guide Version:** 1.0  
**Last Updated:** November 4, 2024  
**Status:** Production Ready

