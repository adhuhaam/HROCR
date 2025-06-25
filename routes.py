import os
from flask import render_template, request, flash, redirect, url_for, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
from app import app, db
from models import PassportRecord
from ocr_processor import OCRProcessor
from passport_parser import PassportParser
from openai_automation import OpenAIAutomation

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/records')
def records():
    records = PassportRecord.query.order_by(PassportRecord.created_at.desc()).all()
    return render_template('records.html', records=records)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the file with OCR
            ocr_processor = OCRProcessor()
            raw_text = ocr_processor.process_file(filepath)
            
            if not raw_text:
                flash('Failed to extract text from the document', 'error')
                return redirect(url_for('index'))
            
            # Parse passport data
            parser = PassportParser()
            passport_data = parser.parse_passport_text(raw_text)
            
            # Enhance with OpenAI if available
            ai_automation = OpenAIAutomation()
            if ai_automation.enabled:
                try:
                    enhanced_data = ai_automation.enhance_passport_extraction(raw_text, passport_data)
                    passport_data.update(enhanced_data)
                    flash('AI enhanced data extraction completed!', 'info')
                except Exception as e:
                    app.logger.warning(f"AI enhancement failed: {str(e)}")
            
            # Create database record
            record = PassportRecord(
                filename=filename,
                passport_number=passport_data.get('passport_number'),
                surname=passport_data.get('surname'),
                given_names=passport_data.get('given_names'),
                nationality=passport_data.get('nationality'),
                date_of_birth=passport_data.get('date_of_birth'),
                place_of_birth=passport_data.get('place_of_birth'),
                sex=passport_data.get('sex'),
                date_of_issue=passport_data.get('date_of_issue'),
                date_of_expiry=passport_data.get('date_of_expiry'),
                issuing_authority=passport_data.get('issuing_authority'),
                emergency_contact=passport_data.get('emergency_contact'),
                phone_number=passport_data.get('phone_number'),
                previous_passport=passport_data.get('previous_passport'),
                raw_text=raw_text
            )
            
            db.session.add(record)
            db.session.commit()
            
            # Clean up uploaded file
            os.remove(filepath)
            
            flash('Passport processed successfully!', 'success')
            return redirect(url_for('records'))
            
        except Exception as e:
            app.logger.error(f"Error processing file: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'error')
            # Clean up file if it exists
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, or PDF files only.', 'error')
        return redirect(url_for('index'))

@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    record = PassportRecord.query.get_or_404(record_id)
    
    if request.method == 'POST':
        # Update record with form data
        record.passport_number = request.form.get('passport_number', '').strip() or None
        record.surname = request.form.get('surname', '').strip() or None
        record.given_names = request.form.get('given_names', '').strip() or None
        record.nationality = request.form.get('nationality', '').strip() or None
        record.date_of_birth = request.form.get('date_of_birth', '').strip() or None
        record.place_of_birth = request.form.get('place_of_birth', '').strip() or None
        record.sex = request.form.get('sex', '').strip() or None
        record.date_of_issue = request.form.get('date_of_issue', '').strip() or None
        record.date_of_expiry = request.form.get('date_of_expiry', '').strip() or None
        record.issuing_authority = request.form.get('issuing_authority', '').strip() or None
        record.emergency_contact = request.form.get('emergency_contact', '').strip() or None
        record.phone_number = request.form.get('phone_number', '').strip() or None
        record.previous_passport = request.form.get('previous_passport', '').strip() or None
        
        try:
            db.session.commit()
            flash('Record updated successfully!', 'success')
            return redirect(url_for('records'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating record: {str(e)}', 'error')
    
    return render_template('edit_record.html', record=record)

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    record = PassportRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('records'))

@app.route('/ai_validate/<int:record_id>')
def ai_validate_record(record_id):
    """Use AI to validate passport record data"""
    record = PassportRecord.query.get_or_404(record_id)
    
    ai_automation = OpenAIAutomation()
    if not ai_automation.enabled:
        flash('AI validation requires OpenAI API key', 'warning')
        return redirect(url_for('records'))
    
    try:
        validation = ai_automation.validate_passport_data(record.to_dict())
        
        if validation['valid']:
            flash('AI validation: Data appears correct ✓', 'success')
        else:
            issues = '; '.join(validation.get('issues', []))
            flash(f'AI validation found issues: {issues}', 'warning')
        
        if validation.get('suggestions'):
            suggestions = '; '.join(validation['suggestions'])
            flash(f'AI suggestions: {suggestions}', 'info')
            
    except Exception as e:
        flash(f'AI validation failed: {str(e)}', 'error')
    
    return redirect(url_for('edit_record', record_id=record_id))

@app.route('/ai_enhance/<int:record_id>')
def ai_enhance_record(record_id):
    """Re-process record with AI enhancement"""
    record = PassportRecord.query.get_or_404(record_id)
    
    ai_automation = OpenAIAutomation()
    if not ai_automation.enabled:
        flash('AI enhancement requires OpenAI API key', 'warning')
        return redirect(url_for('records'))
    
    try:
        # Get current data
        current_data = {
            'passport_number': record.passport_number,
            'surname': record.surname,
            'given_names': record.given_names,
            'nationality': record.nationality,
            'date_of_birth': record.date_of_birth,
            'place_of_birth': record.place_of_birth,
            'sex': record.sex,
            'date_of_issue': record.date_of_issue,
            'date_of_expiry': record.date_of_expiry,
            'issuing_authority': record.issuing_authority,
            'emergency_contact': record.emergency_contact,
            'phone_number': record.phone_number,
            'previous_passport': record.previous_passport
        }
        
        # Enhance with AI
        enhanced_data = ai_automation.enhance_passport_extraction(record.raw_text, current_data)
        
        # Update record
        for field, value in enhanced_data.items():
            if hasattr(record, field) and value:
                setattr(record, field, value)
        
        db.session.commit()
        flash('Record enhanced with AI analysis ✓', 'success')
        
    except Exception as e:
        flash(f'AI enhancement failed: {str(e)}', 'error')
    
    return redirect(url_for('edit_record', record_id=record_id))

@app.route('/generate_document/<int:record_id>')
def generate_document(record_id):
    record = PassportRecord.query.get_or_404(record_id)
    
    try:
        from jinja2 import Template
        import io
        from datetime import datetime
        
        # Job offer letter template
        template_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .header { text-align: center; margin-bottom: 40px; }
                .company-logo { font-size: 24px; font-weight: bold; color: #2c3e50; }
                .date { text-align: right; margin-bottom: 30px; }
                .content { margin-bottom: 30px; }
                .signature { margin-top: 50px; }
                .footer { margin-top: 50px; font-size: 12px; color: #666; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f8f9fa; }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-logo">Your Company Name</div>
                <p>123 Business Street, City, State 12345<br>
                Phone: (555) 123-4567 | Email: hr@company.com</p>
            </div>
            
            <div class="date">
                Date: {{ current_date }}
            </div>
            
            <div class="content">
                <p><strong>To:</strong><br>
                {{ full_name }}<br>
                Passport Number: {{ passport_number }}</p>
                
                <p><strong>Subject: Job Offer Letter</strong></p>
                
                <p>Dear {{ given_names }},</p>
                
                <p>We are pleased to offer you the position of <strong>[Position Title]</strong> at our company. 
                Based on the passport information provided, we have verified your identity and eligibility for employment.</p>
                
                <h3>Personal Information Verified:</h3>
                <table>
                    <tr><th>Full Name</th><td>{{ full_name }}</td></tr>
                    <tr><th>Passport Number</th><td>{{ passport_number }}</td></tr>
                    <tr><th>Nationality</th><td>{{ nationality }}</td></tr>
                    <tr><th>Date of Birth</th><td>{{ date_of_birth }}</td></tr>
                    <tr><th>Sex</th><td>{{ sex }}</td></tr>
                    <tr><th>Passport Expiry</th><td>{{ date_of_expiry }}</td></tr>
                </table>
                
                <h3>Employment Details:</h3>
                <ul>
                    <li><strong>Position:</strong> [Position Title]</li>
                    <li><strong>Department:</strong> [Department Name]</li>
                    <li><strong>Start Date:</strong> [Start Date]</li>
                    <li><strong>Salary:</strong> [Salary Amount]</li>
                    <li><strong>Employment Type:</strong> [Full-time/Part-time]</li>
                </ul>
                
                <p>Please confirm your acceptance of this offer by signing and returning this letter by [Date]. 
                We look forward to welcoming you to our team.</p>
                
                <div class="signature">
                    <p>Sincerely,<br><br>
                    _________________________<br>
                    [HR Manager Name]<br>
                    Human Resources Manager<br>
                    Your Company Name</p>
                </div>
                
                <p>Employee Acceptance:<br><br>
                I, {{ full_name }}, accept the terms and conditions of employment as outlined above.<br><br>
                Signature: _________________________ Date: _____________</p>
            </div>
            
            <div class="footer">
                <p>This document was generated automatically from passport OCR data on {{ current_date }}.</p>
            </div>
        </body>
        </html>
        """
        
        # Prepare template variables
        full_name = f"{record.given_names or ''} {record.surname or ''}".strip()
        if not full_name:
            full_name = "N/A"
            
        template_vars = {
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'full_name': full_name,
            'given_names': record.given_names or 'N/A',
            'surname': record.surname or 'N/A',
            'passport_number': record.passport_number or 'N/A',
            'nationality': record.nationality or 'N/A',
            'date_of_birth': record.date_of_birth or 'N/A',
            'sex': record.sex or 'N/A',
            'date_of_expiry': record.date_of_expiry or 'N/A'
        }
        
        # Try to enhance with AI-generated content
        ai_automation = OpenAIAutomation()
        if ai_automation.enabled:
            try:
                ai_content = ai_automation.generate_document_content(template_vars, "job_offer")
                if ai_content:
                    # Use AI-generated content instead of template
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                            .ai-generated {{ color: #28a745; font-size: 12px; margin-bottom: 20px; }}
                        </style>
                    </head>
                    <body>
                        <div class="ai-generated">✓ AI-Generated Document using OpenAI GPT-4o</div>
                        {ai_content.replace(chr(10), '<br>').replace('  ', '&nbsp;&nbsp;')}
                    </body>
                    </html>
                    """
                else:
                    # Fallback to template
                    template = Template(template_html)
                    html_content = template.render(**template_vars)
            except Exception as e:
                app.logger.warning(f"AI document generation failed: {str(e)}")
                template = Template(template_html)
                html_content = template.render(**template_vars)
        else:
            # Render template
            template = Template(template_html)
            html_content = template.render(**template_vars)
        
        # Create response
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename="job_offer_{record.passport_number or record.id}.html"'
        
        return response
        
    except Exception as e:
        flash(f'Error generating document: {str(e)}', 'error')
        return redirect(url_for('records'))


