#!/usr/bin/env python3
"""
Deployment script for Emotion-Aware Authentication System.

This script helps deploy the system for production use or integration testing.

Usage:
    python deploy.py --mode production --domain yourdomain.com
    python deploy.py --mode development
    python deploy.py --mode integration --port 8080
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path


def create_docker_compose(mode='development', domain='localhost', port=8000):
    """Create docker-compose.yml for deployment."""
    
    compose_content = f"""
version: '3.8'

services:
  emotion-auth-backend:
    build: .
    ports:
      - "{port}:8000"
    environment:
      - MODE={mode}
      - DOMAIN={domain}
      - CORS_ORIGINS=https://{domain},http://{domain}:{port}
    volumes:
      - ./backend/storage:/app/backend/storage
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend:/usr/share/nginx/html
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - emotion-auth-backend
    restart: unless-stopped
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)
    
    print(f"✅ Created docker-compose.yml for {mode} mode")


def create_dockerfile():
    """Create Dockerfile for the backend."""
    
    dockerfile_content = """
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create storage directories
RUN mkdir -p backend/storage/datasets backend/storage/trained_models backend/storage/kd_models backend/storage/alerts

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/docs || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created Dockerfile")


def create_nginx_config(domain='localhost'):
    """Create nginx configuration."""
    
    nginx_content = f"""
events {{
    worker_connections 1024;
}}

http {{
    upstream backend {{
        server emotion-auth-backend:8000;
    }}
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    
    server {{
        listen 80;
        server_name {domain};
        
        # Redirect HTTP to HTTPS in production
        return 301 https://$server_name$request_uri;
    }}
    
    server {{
        listen 443 ssl http2;
        server_name {domain};
        
        # SSL configuration (add your certificates)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
        
        # Serve frontend files
        location /web/ {{
            alias /usr/share/nginx/html/;
            try_files $uri $uri/ =404;
            
            # Cache static assets
            location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {{
                expires 1y;
                add_header Cache-Control "public, immutable";
            }}
        }}
        
        # API endpoints with rate limiting
        location /api/auth/ {{
            limit_req zone=auth burst=3 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
        
        location /api/ {{
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
        
        # Docs and health check
        location /docs {{
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }}
        
        location /health {{
            proxy_pass http://backend/docs;
            proxy_set_header Host $host;
        }}
    }}
}}
"""
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_content)
    
    print(f"✅ Created nginx.conf for {domain}")


def create_env_file(mode='development', domain='localhost'):
    """Create environment configuration file."""
    
    env_content = f"""
# Emotion-Aware Authentication Configuration
MODE={mode}
DOMAIN={domain}
DEBUG={'true' if mode == 'development' else 'false'}

# CORS settings
CORS_ORIGINS=https://{domain},http://{domain}:8000,http://localhost:8000

# Database
DATABASE_URL=sqlite:///./backend/storage/app.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL={'DEBUG' if mode == 'development' else 'INFO'}
LOG_FILE=./logs/emotion-auth.log

# Model settings
MODEL_PATH=./backend/storage/trained_models
DATA_PATH=./backend/storage/datasets

# Alert settings
ALERT_EMAIL_ENABLED=false
ALERT_EMAIL_SMTP_HOST=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_TO=admin@yourdomain.com
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file for {mode} mode")


def create_integration_package():
    """Create integration package for distribution."""
    
    package_dir = Path('emotion-auth-integration')
    package_dir.mkdir(exist_ok=True)
    
    # Copy SDK
    import shutil
    if Path('frontend/emotion-auth-sdk.js').exists():
        shutil.copy('frontend/emotion-auth-sdk.js', package_dir / 'emotion-auth-sdk.js')
    if Path('backend/api_wrapper.py').exists():
        shutil.copy('backend/api_wrapper.py', package_dir / 'api_wrapper.py')
    if Path('frontend/integration-example.html').exists():
        shutil.copy('frontend/integration-example.html', package_dir / 'example.html')
    if Path('INTEGRATION_GUIDE.md').exists():
        shutil.copy('INTEGRATION_GUIDE.md', package_dir / 'README.md')
    
    # Create package.json for npm
    package_json = {
        "name": "emotion-auth-sdk",
        "version": "1.0.0",
        "description": "Emotion-Aware Authentication SDK for web integration",
        "main": "emotion-auth-sdk.js",
        "scripts": {
            "test": "echo \"Error: no test specified\" && exit 1"
        },
        "keywords": ["authentication", "emotion", "biometrics", "security", "AI"],
        "author": "Emotion-Auth Team",
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "https://github.com/your-org/emotion-auth-sdk"
        },
        "files": [
            "emotion-auth-sdk.js",
            "api_wrapper.py",
            "example.html",
            "README.md"
        ]
    }
    
    with open(package_dir / 'package.json', 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Create Python setup.py
    setup_py = """
from setuptools import setup, find_packages

setup(
    name="emotion-auth-api",
    version="1.0.0",
    description="Python API wrapper for Emotion-Aware Authentication",
    author="Emotion-Auth Team",
    author_email="contact@emotion-auth.com",
    url="https://github.com/your-org/emotion-auth-api",
    py_modules=["api_wrapper"],
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
"""
    
    with open(package_dir / 'setup.py', 'w') as f:
        f.write(setup_py)
    
    print(f"✅ Created integration package in {package_dir}")
    print(f"   - JavaScript SDK: emotion-auth-sdk.js")
    print(f"   - Python API wrapper: api_wrapper.py")
    print(f"   - Example HTML: example.html")
    print(f"   - Documentation: README.md")
    print(f"   - NPM package.json")
    print(f"   - Python setup.py")


def run_deployment(mode='development', domain='localhost', port=8000, skip_docker=False):
    """Run the deployment process."""
    
    print(f"🚀 Deploying Emotion-Aware Authentication System")
    print(f"   Mode: {mode}")
    print(f"   Domain: {domain}")
    print(f"   Port: {port}")
    print("="*60)
    
    # Create deployment files
    if not skip_docker:
        create_dockerfile()
        create_docker_compose(mode, domain, port)
        create_nginx_config(domain)
    
    create_env_file(mode, domain)
    
    # Create integration package
    create_integration_package()
    
    print("\n📦 Deployment files created:")
    if not skip_docker:
        print("   - Dockerfile")
        print("   - docker-compose.yml")
        print("   - nginx.conf")
    print("   - .env")
    print("   - emotion-auth-integration/ (SDK package)")
    
    if mode == 'production':
        print("\n⚠️  Production deployment checklist:")
        print("   1. Add SSL certificates to ./ssl/ directory")
        print("   2. Update SECRET_KEY in .env file")
        print("   3. Configure email alerts in .env")
        print("   4. Review and adjust rate limits in nginx.conf")
        print("   5. Set up database backups")
        print("   6. Configure monitoring and logging")
        print("\n🚀 To deploy:")
        print("   docker-compose up -d")
        print("\n📊 To view logs:")
        print("   docker-compose logs -f")
    
    elif mode == 'development':
        print("\n🚀 To start development server:")
        print("   python -m uvicorn backend.main:app --reload --port", port)
        print("\n📊 API docs will be available at:")
        print(f"   http://localhost:{port}/docs")
    
    elif mode == 'integration':
        print("\n📦 Integration package ready!")
        print("\nFor JavaScript integration:")
        print("   1. Copy emotion-auth-integration/emotion-auth-sdk.js to your project")
        print("   2. Include it in your HTML: <script src='emotion-auth-sdk.js'></script>")
        print("   3. See example.html for usage")
        print("\nFor Python integration:")
        print("   1. pip install ./emotion-auth-integration")
        print("   2. from api_wrapper import EmotionAuthAPI")
        print("   3. See api_wrapper.py for usage examples")


def main():
    parser = argparse.ArgumentParser(
        description='Deploy Emotion-Aware Authentication System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py --mode development
  python deploy.py --mode production --domain auth.example.com
  python deploy.py --mode integration --port 8080
  python deploy.py --mode development --skip-docker
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['development', 'production', 'integration'],
        default='development',
        help='Deployment mode (default: development)'
    )
    
    parser.add_argument(
        '--domain',
        default='localhost',
        help='Domain name for deployment (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port number for the backend (default: 8000)'
    )
    
    parser.add_argument(
        '--skip-docker',
        action='store_true',
        help='Skip Docker-related files (Dockerfile, docker-compose.yml, nginx.conf)'
    )
    
    args = parser.parse_args()
    
    try:
        run_deployment(
            mode=args.mode,
            domain=args.domain,
            port=args.port,
            skip_docker=args.skip_docker
        )
        print("\n✅ Deployment preparation complete!")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
