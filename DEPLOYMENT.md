# HR Management System - Raspberry Pi Deployment Guide

## Overview
This comprehensive HR management system with passport OCR capabilities is ready for deployment to your Raspberry Pi running Ubuntu Server.

## System Features
- ✅ Passport OCR with Tesseract and AI enhancement
- ✅ Automated job offer email generation and sending
- ✅ AI-powered HR query responses
- ✅ Intelligent leave request evaluation
- ✅ Employee management dashboard
- ✅ Document generation and verification
- ✅ Emergency contact and phone number extraction

## Deployment Steps

### 1. Replit Deployment (Current)
The system is currently running on Replit and ready for deployment:
- Click the "Deploy" button in your Replit dashboard
- The system will be available at a `.replit.app` domain
- All dependencies and configuration are handled automatically

### 2. Raspberry Pi Setup

#### Prerequisites
```bash
# Update your Raspberry Pi Ubuntu Server
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and dependencies
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install system dependencies for OCR
sudo apt install tesseract-ocr tesseract-ocr-eng -y
sudo apt install poppler-utils -y

# Install PostgreSQL (recommended for production)
sudo apt install postgresql postgresql-contrib -y
```

#### Git Setup
```bash
# Clone your repository (replace with your actual repo URL)
git clone https://github.com/yourusername/passport-ocr-hr.git
cd passport-ocr-hr

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Environment Variables
Create a `.env` file on your Raspberry Pi:
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/passport_ocr_hr
SESSION_SECRET=your-secret-key-here

# AI and Email Services (optional but recommended)
OPENAI_API_KEY=your-openai-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
COMPANY_EMAIL=hr@yourcompany.com
COMPANY_NAME=Your Company Name

# Production Settings
FLASK_ENV=production
```

#### Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres createdb passport_ocr_hr
sudo -u postgres createuser your_username
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE passport_ocr_hr TO your_username;"

# Run the application to create tables
python main.py
```

#### System Service Setup
Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/passport-ocr-hr.service
```

Service file content:
```ini
[Unit]
Description=Passport OCR HR Management System
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/passport-ocr-hr
Environment=PATH=/home/ubuntu/passport-ocr-hr/venv/bin
ExecStart=/home/ubuntu/passport-ocr-hr/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable passport-ocr-hr
sudo systemctl start passport-ocr-hr
sudo systemctl status passport-ocr-hr
```

#### Nginx Reverse Proxy (Optional)
For production deployment with domain name:

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/passport-ocr-hr
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/passport-ocr-hr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Git Repository Setup

### Initialize Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: HR Management System with Passport OCR"

# Add remote repository (create on GitHub/GitLab first)
git remote add origin https://github.com/yourusername/passport-ocr-hr.git
git branch -M main
git push -u origin main
```

### .gitignore File
```gitignore
# Environment variables
.env
.env.local

# Database
instance/
*.db
*.sqlite

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
pip-log.txt
pip-delete-this-directory.txt

# Uploads (optional - exclude uploaded files)
uploads/*
!uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

## Production Considerations

### Security
- [ ] Change default session secret
- [ ] Set up HTTPS with SSL certificate
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Backup strategy for database

### Performance
- [ ] Configure Gunicorn workers based on CPU cores
- [ ] Set up Redis for session storage (optional)
- [ ] Database connection pooling
- [ ] Log rotation

### Monitoring
- [ ] Set up application logging
- [ ] Monitor system resources
- [ ] Database backup automation
- [ ] Email notifications for errors

## Maintenance Commands

```bash
# Update system
git pull origin main
sudo systemctl restart passport-ocr-hr

# View logs
sudo journalctl -u passport-ocr-hr -f

# Database backup
pg_dump passport_ocr_hr > backup_$(date +%Y%m%d).sql

# Check service status
sudo systemctl status passport-ocr-hr
```

## Features Available

### 1. Passport Processing
- Upload PDF or image files
- Extract personal information automatically
- AI-enhanced data accuracy
- Manual editing and validation

### 2. HR Automation
- Automated job offer email generation
- AI query response system
- Leave request evaluation with AI
- Employee management dashboard

### 3. AI Integration
- OpenAI GPT-4o for text enhancement
- Smart document validation
- Automated email content generation
- Intelligent leave approval recommendations

## Support and Development

For future development and support:
1. Use Git for version control and collaboration
2. Create feature branches for new developments
3. Test changes thoroughly before deployment
4. Monitor system performance and logs
5. Keep API keys and secrets secure

The system is production-ready and scalable for your HR management needs on Raspberry Pi.