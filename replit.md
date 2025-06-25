# Passport OCR System

## Overview

This is a Flask-based web application that provides Optical Character Recognition (OCR) capabilities for passport documents. Users can upload passport images or PDF files, and the system extracts structured information such as passport number, personal details, and document dates using Tesseract OCR and custom parsing algorithms.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with SQLAlchemy ORM
- **Database**: SQLite for development (configurable for PostgreSQL in production)
- **OCR Engine**: Tesseract OCR with pytesseract Python wrapper
- **File Processing**: PIL (Pillow) for image manipulation, pdf2image for PDF conversion
- **Web Server**: Gunicorn for production deployment

### Frontend Architecture
- **Templates**: Jinja2 templating with responsive Bootstrap UI
- **Styling**: Bootstrap with custom CSS for drag-and-drop interface
- **JavaScript**: Vanilla JavaScript for file upload interactions

## Key Components

### 1. Application Core (`app.py`)
- Flask application factory with SQLAlchemy configuration
- Database initialization and connection management
- Upload folder configuration (16MB max file size)
- Session management with secret key

### 2. Data Models (`models.py`)
- `PassportRecord`: Main entity storing extracted passport information
  - Personal details (name, nationality, dates)
  - Document metadata (filename, processing status)
  - Raw OCR text for debugging

### 3. OCR Processing (`ocr_processor.py`)
- Handles multiple file formats (PNG, JPG, JPEG, PDF)
- Image preprocessing for improved OCR accuracy
- Tesseract configuration optimized for passport documents
- PDF to image conversion pipeline

### 4. Data Parsing (`passport_parser.py`)
- Regex-based extraction of structured fields from raw OCR text
- Support for multiple passport formats and layouts
- Field validation and normalization
- Date parsing and formatting

### 5. Web Routes (`routes.py`)
- File upload handling with security validation
- OCR processing workflow integration
- Record management and display
- RESTful API endpoints for data access

## Data Flow

1. **File Upload**: User uploads passport document via web interface
2. **Security Check**: File type and size validation
3. **OCR Processing**: 
   - Image enhancement and preprocessing
   - Text extraction using Tesseract
4. **Data Parsing**: 
   - Regex pattern matching on raw text
   - Field extraction and validation
5. **Database Storage**: Structured data saved to PassportRecord table
6. **Result Display**: Processed information shown to user

## External Dependencies

### Core Libraries
- `Flask`: Web framework and routing
- `SQLAlchemy`: Database ORM and migrations
- `pytesseract`: Tesseract OCR Python wrapper
- `Pillow`: Image processing and manipulation
- `pdf2image`: PDF to image conversion
- `PyPDF2`: PDF text extraction

### System Dependencies
- `tesseract`: OCR engine (installed via Nix)
- `poppler-utils`: PDF processing utilities
- `postgresql`: Database server (available for production)

### UI Dependencies
- `Bootstrap`: Responsive CSS framework (CDN)
- `Font Awesome`: Icon library (CDN)

## Deployment Strategy

### Development Environment
- SQLite database for local development
- Flask development server with auto-reload
- Debug logging enabled

### Production Environment
- Gunicorn WSGI server with auto-scaling
- PostgreSQL database (configured via DATABASE_URL)
- Connection pooling with health checks
- Static file serving optimization

### Container Configuration
- Nix environment with Python 3.11
- Pre-installed system dependencies for OCR
- Automated deployment via Replit

## Changelog
- June 25, 2025: Initial setup with basic OCR functionality
- June 25, 2025: Enhanced Tesseract OCR with advanced image preprocessing
- June 25, 2025: Added comprehensive passport data extraction patterns
- June 25, 2025: Added record editing functionality with all requested fields
- June 25, 2025: Integrated OpenAI GPT-4o for AI-powered data enhancement
- June 25, 2025: Added AI validation and document generation features
- June 25, 2025: Extended database model with emergency contact, phone, previous passport fields
- June 25, 2025: Expanded into full HR management system with automated workflows
- June 25, 2025: Added automated email job offers, AI query responses, and leave management
- June 25, 2025: Implemented HR dashboard with employee management and reporting features

## User Preferences

Preferred communication style: Simple, everyday language.