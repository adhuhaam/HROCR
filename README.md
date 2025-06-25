# HR Management System with Passport OCR

A comprehensive HR management system that processes passport documents using OCR technology and provides automated workflows for recruitment, leave management, and query handling.

## Features

### Core Capabilities
- **Passport OCR Processing**: Extract personal information from passport images and PDFs
- **AI-Enhanced Extraction**: Uses OpenAI GPT-4o for improved accuracy and data validation
- **Automated Job Offers**: Generate and email professional job offer letters
- **HR Query Assistant**: AI-powered responses to common HR questions
- **Leave Management**: Intelligent evaluation and approval of leave requests
- **Employee Dashboard**: Comprehensive HR management interface

### Technology Stack
- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **OCR**: Tesseract with advanced image preprocessing
- **AI**: OpenAI GPT-4o integration
- **Email**: SendGrid for automated communications
- **Frontend**: Bootstrap with responsive design
- **Deployment**: Gunicorn with Nginx reverse proxy

## Quick Start

### 1. Local Development
```bash
git clone <repository-url>
cd hr-management-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 2. Environment Configuration
Create `.env` file:
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
SESSION_SECRET=your-secret-key
OPENAI_API_KEY=your-openai-key
SENDGRID_API_KEY=your-sendgrid-key
COMPANY_EMAIL=hr@company.com
COMPANY_NAME=Your Company
```

### 3. Database Setup
```bash
# PostgreSQL
createdb hr_management
python -c "from app import db; db.create_all()"
```

## Deployment

### Raspberry Pi Deployment
See `gg.md` for complete hosting guide including:
- Ubuntu Server setup
- PostgreSQL configuration
- Nginx reverse proxy
- SSL certificate setup
- System service configuration

### Cloud Deployment
- **Replit**: Click "Deploy" button (easiest)
- **DigitalOcean/AWS**: Follow cloud VPS instructions in `gg.md`
- **Docker**: Use provided Dockerfile and docker-compose.yml

## System Requirements

### Minimum Hardware
- 2GB RAM
- 10GB storage
- Multi-core CPU recommended

### Software Dependencies
- Python 3.11+
- PostgreSQL 13+
- Tesseract OCR
- Poppler utilities

## Usage

### 1. Passport Processing
1. Upload passport image/PDF via web interface
2. System extracts personal information automatically
3. AI enhances accuracy and fills missing fields
4. Review and edit extracted data
5. Generate documents or create job offers

### 2. HR Automation
1. **Job Offers**: Create offers directly from passport records
2. **Query Responses**: Submit questions to AI assistant
3. **Leave Requests**: Intelligent evaluation with auto-approval
4. **Employee Management**: Dashboard for HR operations

### 3. API Integration
The system provides REST endpoints for:
- Passport data retrieval
- Job offer management
- Leave request processing
- HR query handling

## Configuration

### Security Settings
- Session management with secure cookies
- CSRF protection
- File upload validation
- SQL injection prevention

### Performance Tuning
- Database connection pooling
- Image preprocessing optimization
- Gunicorn worker configuration
- Nginx caching headers

## Monitoring

### Application Logs
```bash
# System service logs
sudo journalctl -u hr-management -f

# Application logs
tail -f logs/application.log
```

### Health Checks
- Database connectivity
- OCR engine status
- AI service availability
- Email service status

## Backup and Recovery

### Automated Backups
```bash
# Database backup
pg_dump hr_management > backup.sql

# File backup
tar -czf uploads_backup.tar.gz uploads/
```

### Disaster Recovery
- Database restore procedures
- File system recovery
- Service restart protocols

## Development

### Project Structure
```
├── app.py              # Flask application factory
├── main.py             # Application entry point
├── models.py           # Database models (passport records)
├── models_hr.py        # HR-specific models
├── routes.py           # Web routes and API endpoints
├── ocr_processor.py    # OCR and image processing
├── passport_parser.py  # Data extraction logic
├── openai_automation.py # AI integration
├── hr_automation.py    # HR workflow automation
├── templates/          # HTML templates
├── static/            # CSS, JS, images
└── uploads/           # File upload directory
```

### Adding Features
1. Create feature branch
2. Add models to `models_hr.py`
3. Implement routes in `routes.py`
4. Add templates if needed
5. Test thoroughly
6. Deploy via Git

### API Documentation
- `/api/records` - Passport record management
- `/api/offers` - Job offer operations
- `/api/queries` - HR query processing
- `/api/leaves` - Leave request handling

## Troubleshooting

### Common Issues
- **OCR not working**: Check Tesseract installation
- **Database errors**: Verify PostgreSQL connection
- **Email failures**: Validate SendGrid configuration
- **AI errors**: Check OpenAI API key

### Performance Issues
- Monitor database queries
- Check file upload sizes
- Review worker process count
- Optimize image processing

## Support

For technical support:
1. Check logs for error messages
2. Verify configuration settings
3. Test individual components
4. Review deployment guide

## License

This project is proprietary software for internal HR management use.

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Follow code review process

---

For complete deployment instructions, see `gg.md`
For technical architecture details, see `replit.md`