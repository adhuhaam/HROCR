from app import db
from datetime import datetime

class PassportRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    
    # Passport fields
    passport_number = db.Column(db.String(50))
    surname = db.Column(db.String(100))
    given_names = db.Column(db.String(200))
    nationality = db.Column(db.String(50))
    date_of_birth = db.Column(db.String(20))
    place_of_birth = db.Column(db.String(100))
    sex = db.Column(db.String(10))
    date_of_issue = db.Column(db.String(20))
    date_of_expiry = db.Column(db.String(20))
    issuing_authority = db.Column(db.String(100))
    
    # Metadata
    raw_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(20), default='completed')
    
    def __repr__(self):
        return f'<PassportRecord {self.passport_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'passport_number': self.passport_number,
            'surname': self.surname,
            'given_names': self.given_names,
            'nationality': self.nationality,
            'date_of_birth': self.date_of_birth,
            'place_of_birth': self.place_of_birth,
            'sex': self.sex,
            'date_of_issue': self.date_of_issue,
            'date_of_expiry': self.date_of_expiry,
            'issuing_authority': self.issuing_authority,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'processing_status': self.processing_status
        }
