import os
from flask import render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import PassportRecord
from ocr_processor import OCRProcessor
from passport_parser import PassportParser

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

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    record = PassportRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('records'))

import time
