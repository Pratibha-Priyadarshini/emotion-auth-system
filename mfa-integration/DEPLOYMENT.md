# 🚀 Production Deployment Guide

Complete guide for deploying emotion-aware MFA to production.

---

## Pre-Deployment Checklist

### Security

- [ ] All connections use HTTPS/TLS
- [ ] API keys stored in environment variables (not in code)
- [ ] CORS configured to allow only your domains
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (if using database)
- [ ] XSS protection headers configured
- [ ] CSRF tokens implemented
- [ ] Session management secure
- [ ] Audit logging enabled

### Performance

- [ ] CDN configured for static assets
- [ ] Image compression enabled
- [ ] API response caching configured
- [ ] Database indexes optimized
- [ ] Load balancing configured (if needed)
- [ ] Auto-scaling rules defined
- [ ] Connection pooling enabled
- [ ] Timeout values optimized

### Monitoring

- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring enabled
- [ ] Uptime monitoring configured
- [ ] Alert notifications set up
- [ ] Log aggregation configured
- [ ] Metrics dashboard created
- [ ] Health check endpoints working

### Backup & Recovery

- [ ] Database backups automated
- [ ] Backup restoration tested
- [ ] Disaster recovery plan documented
- [ ] Failover procedures defined
- [ ] Data retention policy set

### Compliance

- [ ] Privacy policy updated
- [ ] Terms of service updated
- [ ] GDPR compliance verified (if applicable)
- [ ] Data encryption at rest
- [ ] Data encryption in transit
- [ ] User consent mechanisms in place
- [ ] Data deletion procedures defined

---

## Deployment Options

### Option 1: Docker Deployment

#### 1.1 Build Docker Image

```bash
# Build backend image
docker build -t emotion-auth-backend:latest .

# Test locally
docker run -p 8000:8000 emotion-auth-backend:latest
```

#### 1.2 Docker Compose

```yaml
version: '3.8'

services:
  backend:
    image: emotion-auth-backend:latest
    ports:
      - "8000:8000"
    environment:
      - MODE=production
      - API_KEY=${API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./storage:/app/backend/storage
      - ./logs:/app/logs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./frontend:/usr/share/nginx/html
    depends_on:
      - backend
    restart: unless-stopped
```

#### 1.3 Deploy

```bash
docker-compose up -d
```

---

### Option 2: Cloud Deployment

#### AWS Deployment

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Deploy using Elastic Beanstalk
eb init emotion-auth-mfa
eb create production-env
eb deploy
```

**AWS Services:**
- **EC2** - Application servers
- **RDS** - Database
- **S3** - Static assets and backups
- **CloudFront** - CDN
- **Route 53** - DNS
- **CloudWatch** - Monitoring
- **ELB** - Load balancing

#### Azure Deployment

```bash
# Install Azure CLI
pip install azure-cli

# Login
az login

# Create resource group
az group create --name emotion-auth-rg --location eastus

# Deploy web app
az webapp up --name emotion-auth-app --resource-group emotion-auth-rg
```

#### Google Cloud Deployment

```bash
# Install gcloud CLI
# Follow: https://cloud.google.com/sdk/docs/install

# Initialize
gcloud init

# Deploy to App Engine
gcloud app deploy
```

---

### Option 3: VPS Deployment (DigitalOcean, Linode, etc.)

#### 3.1 Server Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip nginx certbot python3-certbot-nginx

# Create app user
useradd -m -s /bin/bash emotion-auth
```

#### 3.2 Deploy Application

```bash
# Clone repository
cd /home/emotion-auth
git clone https://github.com/your-org/emotion-auth-mfa.git
cd emotion-auth-mfa

# Install Python dependencies
pip3 install -r backend/requirements.txt

# Create systemd service
cat > /etc/systemd/system/emotion-auth.service << EOF
[Unit]
Description=Emotion Auth MFA Service
After=network.target

[Service]
User=emotion-auth
WorkingDirectory=/home/emotion-auth/emotion-auth-mfa
ExecStart=/usr/local/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
systemctl enable emotion-auth
systemctl start emotion-auth
```

#### 3.3 Configure Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL certificates (from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=mfa:10m rate=5r/m;
    
    # Frontend
    location / {
        root /home/emotion-auth/emotion-auth-mfa/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # API
    location /api/ {
        limit_req zone=mfa burst=3 nodelay;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3.4 Get SSL Certificate

```bash
# Get certificate from Let's Encrypt
certbot --nginx -d your-domain.com

# Auto-renewal
certbot renew --dry-run
```

---

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```bash
# Application
MODE=production
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this

# API
API_URL=https://your-domain.com
API_KEY=your-api-key-change-this
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/emotion_auth

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# Email Alerts
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_SMTP_HOST=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=alerts@your-domain.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_TO=admin@your-domain.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
LOG_FILE=/var/log/emotion-auth/app.log

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Security
SESSION_TIMEOUT=1800
MFA_CACHE_DURATION=300
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900
```

---

## Monitoring & Alerts

### Setup Monitoring

#### Using Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
```

#### Configure Alerts

```python
# In your backend, add monitoring endpoints
from prometheus_client import Counter, Histogram, generate_latest

auth_attempts = Counter('auth_attempts_total', 'Total authentication attempts')
auth_success = Counter('auth_success_total', 'Successful authentications')
auth_failures = Counter('auth_failures_total', 'Failed authentications')
auth_duration = Histogram('auth_duration_seconds', 'Authentication duration')

@app.get('/metrics')
def metrics():
    return Response(generate_latest(), media_type='text/plain')
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    image: emotion-auth-backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
    environment:
      - MODE=production
      
  load-balancer:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

### Load Balancer Configuration

```nginx
upstream backend {
    least_conn;
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}

server {
    listen 443 ssl http2;
    
    location /api/ {
        proxy_pass http://backend;
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }
}
```

---

## Backup Strategy

### Automated Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
pg_dump emotion_auth > $BACKUP_DIR/db_$DATE.sql

# Backup storage
tar -czf $BACKUP_DIR/storage_$DATE.tar.gz /app/backend/storage

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /app/logs

# Upload to S3
aws s3 cp $BACKUP_DIR/ s3://your-backup-bucket/ --recursive

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -mtime +30 -delete
```

### Cron Job

```bash
# Add to crontab
0 2 * * * /home/emotion-auth/backup.sh
```

---

## Security Hardening

### Firewall Rules

```bash
# UFW (Ubuntu)
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Fail2Ban

```bash
# Install
apt install fail2ban

# Configure
cat > /etc/fail2ban/jail.local << EOF
[emotion-auth]
enabled = true
port = 80,443
filter = emotion-auth
logpath = /var/log/emotion-auth/app.log
maxretry = 5
bantime = 3600
EOF
```

---

## Testing in Production

### Smoke Tests

```bash
#!/bin/bash
# smoke-test.sh

API_URL="https://your-domain.com"

# Test health endpoint
curl -f $API_URL/docs || exit 1

# Test API
curl -f -X POST $API_URL/api/test/simulate?stress_level=0.3 || exit 1

echo "✅ All smoke tests passed"
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 https://your-domain.com/api/test/simulate

# Using wrk
wrk -t12 -c400 -d30s https://your-domain.com/api/test/simulate
```

---

## Rollback Procedure

```bash
# If deployment fails, rollback:

# Docker
docker-compose down
docker-compose -f docker-compose.backup.yml up -d

# Git
git revert HEAD
git push origin main

# Systemd
systemctl stop emotion-auth
cd /home/emotion-auth/emotion-auth-mfa
git checkout previous-stable-tag
systemctl start emotion-auth
```

---

## Support & Maintenance

### Regular Maintenance Tasks

- **Daily:** Check logs for errors
- **Weekly:** Review security alerts
- **Monthly:** Update dependencies
- **Quarterly:** Security audit
- **Yearly:** Disaster recovery drill

### Monitoring Checklist

- [ ] API response times < 500ms
- [ ] Error rate < 1%
- [ ] CPU usage < 70%
- [ ] Memory usage < 80%
- [ ] Disk usage < 80%
- [ ] SSL certificate valid
- [ ] Backups completing successfully

---

## Documentation

Maintain these documents:

1. **Architecture Diagram** - System overview
2. **API Documentation** - Endpoint reference
3. **Runbook** - Common operations
4. **Incident Response Plan** - Emergency procedures
5. **Change Log** - Version history

---

## Support Contacts

- **Technical Support:** support@emotion-auth.com
- **Security Issues:** security@emotion-auth.com
- **Emergency:** +1-XXX-XXX-XXXX

---

**Good luck with your deployment! 🚀**
