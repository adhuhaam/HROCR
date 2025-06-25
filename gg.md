# Complete Hosting Guide for HR Management System

## Overview
This comprehensive guide covers hosting your HR Management System with Passport OCR on various platforms including Raspberry Pi, cloud services, and local servers.

## 🚀 Quick Deployment Options

### Option 1: Replit Cloud Hosting (Easiest)
```bash
# Already configured and ready
# Just click "Deploy" in Replit dashboard
# Your app will be available at: https://your-app-name.replit.app
```

**Pros:**
- Zero configuration required
- Automatic SSL and domain
- Built-in database management
- Instant deployment

**Cons:**
- Monthly subscription cost
- Less control over server configuration

### Option 2: Raspberry Pi Self-Hosting (Recommended)
Perfect for local office deployment with full control.

#### Hardware Requirements
- Raspberry Pi 4 (4GB+ RAM recommended)
- MicroSD card (32GB+ Class 10)
- Stable internet connection
- Optional: External storage for backups

#### Software Setup
```bash
# 1. Install Ubuntu Server on Raspberry Pi
# Download from: https://ubuntu.com/download/raspberry-pi

# 2. Initial server setup
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-pip python3.11-venv -y
sudo apt install tesseract-ocr tesseract-ocr-eng poppler-utils -y
sudo apt install postgresql postgresql-contrib nginx -y
sudo apt install git curl wget -y

# 3. Create application user
sudo useradd -m -s /bin/bash hrapp
sudo usermod -aG sudo hrapp
sudo su - hrapp

# 4. Clone and setup application
git clone https://github.com/yourusername/hr-management-system.git
cd hr-management-system
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Database Configuration
```bash
# Setup PostgreSQL
sudo -u postgres createdb hr_management
sudo -u postgres createuser hrapp_user
sudo -u postgres psql -c "ALTER USER hrapp_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hr_management TO hrapp_user;"

# Configure environment
cat > .env << EOF
DATABASE_URL=postgresql://hrapp_user:secure_password@localhost/hr_management
SESSION_SECRET=$(openssl rand -hex 32)
FLASK_ENV=production
OPENAI_API_KEY=your_openai_key_here
SENDGRID_API_KEY=your_sendgrid_key_here
COMPANY_EMAIL=hr@yourcompany.com
COMPANY_NAME=Your Company Name
EOF
```

#### System Service Setup
```bash
# Create systemd service
sudo tee /etc/systemd/system/hr-management.service << EOF
[Unit]
Description=HR Management System
After=network.target postgresql.service

[Service]
Type=exec
User=hrapp
Group=hrapp
WorkingDirectory=/home/hrapp/hr-management-system
Environment=PATH=/home/hrapp/hr-management-system/venv/bin
EnvironmentFile=/home/hrapp/hr-management-system/.env
ExecStart=/home/hrapp/hr-management-system/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable hr-management
sudo systemctl start hr-management
sudo systemctl status hr-management
```

#### Nginx Reverse Proxy
```bash
# Configure Nginx
sudo tee /etc/nginx/sites-available/hr-management << EOF
server {
    listen 80;
    server_name your-domain.com 192.168.1.100;  # Your Pi's IP

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /static {
        alias /home/hrapp/hr-management-system/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/hr-management /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Cloud VPS Hosting (Scalable)

#### DigitalOcean/Linode/Vultr Setup
```bash
# 1. Create Ubuntu 22.04 droplet ($5-10/month)
# 2. Connect via SSH
ssh root@your-server-ip

# 3. Setup application (same as Raspberry Pi steps above)
# 4. Configure firewall
ufw allow ssh
ufw allow http
ufw allow https
ufw enable

# 5. Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

#### AWS EC2 Setup
```bash
# 1. Launch t2.micro or t3.small instance
# 2. Configure security groups (HTTP, HTTPS, SSH)
# 3. Follow Ubuntu setup steps
# 4. Use RDS for managed PostgreSQL (optional)
```

### Option 4: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:5000"
    environment:
      - DATABASE_URL=postgresql://hr_user:password@db:5432/hr_management
      - SESSION_SECRET=your-secret-key
      - OPENAI_API_KEY=your-openai-key
      - SENDGRID_API_KEY=your-sendgrid-key
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=hr_management
      - POSTGRES_USER=hr_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 🔧 Configuration Guide

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/database
SESSION_SECRET=random-64-character-string

# Optional but recommended
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG....
COMPANY_EMAIL=hr@company.com
COMPANY_NAME=Your Company

# Production settings
FLASK_ENV=production
PYTHONPATH=/app
```

### Database Configuration
```python
# Production database URL examples:
# PostgreSQL: postgresql://user:pass@localhost:5432/dbname
# SQLite: sqlite:///app.db
# MySQL: mysql://user:pass@localhost:3306/dbname
```

### SSL Certificate Setup
```bash
# Free SSL with Let's Encrypt
sudo certbot --nginx -d yourdomain.com

# Manual SSL certificate
sudo mkdir /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt
```

## 📱 Mobile Access Setup

### Responsive Design
The system is already mobile-responsive, but for better mobile experience:

```nginx
# Add mobile-specific headers
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header X-Forwarded-Proto $scheme;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
}
```

### PWA Configuration (Optional)
Create a Progressive Web App for mobile installation:

```json
{
  "name": "HR Management System",
  "short_name": "HR Manager",
  "description": "Complete HR management with passport OCR",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#007bff",
  "background_color": "#ffffff",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

## 🔒 Security Configuration

### Firewall Setup
```bash
# Ubuntu UFW
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5000/tcp  # Block direct access to app
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y
```

### Application Security
```python
# Security headers in Nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## 📊 Monitoring and Maintenance

### Log Management
```bash
# Application logs
sudo journalctl -u hr-management -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Database logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Backup Strategy
```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/hrapp/backups"

# Database backup
pg_dump hr_management > $BACKUP_DIR/db_backup_$DATE.sql

# File backup
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /home/hrapp/hr-management-system/uploads

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Performance Monitoring
```bash
# System resources
htop
df -h
free -h

# Application performance
curl -o /dev/null -s -w "%{time_total}\n" http://localhost/

# Database performance
sudo -u postgres psql hr_management -c "SELECT * FROM pg_stat_activity;"
```

## 🚨 Troubleshooting

### Common Issues
```bash
# Service won't start
sudo journalctl -u hr-management --no-pager -l

# Permission issues
sudo chown -R hrapp:hrapp /home/hrapp/hr-management-system

# Database connection issues
sudo -u postgres psql -c "SELECT version();"

# OCR not working
tesseract --version
sudo apt install tesseract-ocr-eng

# Nginx configuration test
sudo nginx -t
```

### Performance Optimization
```bash
# Increase file upload limits
# In /etc/nginx/nginx.conf
client_max_body_size 50M;

# Optimize PostgreSQL
# In /etc/postgresql/15/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
```

## 📋 Maintenance Checklist

### Daily
- [ ] Check service status
- [ ] Monitor disk space
- [ ] Review application logs

### Weekly
- [ ] Database backup verification
- [ ] Security updates
- [ ] Performance monitoring

### Monthly
- [ ] Full system backup
- [ ] SSL certificate renewal check
- [ ] Log rotation and cleanup
- [ ] Security audit

## 🔗 Integration Options

### External Services
- **Email**: SendGrid, Mailgun, AWS SES
- **Storage**: AWS S3, Google Cloud Storage
- **Monitoring**: Datadog, New Relic, Prometheus
- **Backup**: AWS Backup, Backblaze B2

### API Integrations
- LDAP/Active Directory for authentication
- Slack/Teams for notifications
- Calendar systems for leave management
- Payroll systems integration

This complete hosting guide ensures your HR Management System runs reliably and securely across different deployment scenarios.