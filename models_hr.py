from app import db
from datetime import datetime

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passport_record_id = db.Column(db.Integer, db.ForeignKey('passport_record.id'), nullable=True)
    
    # Employee Information
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    salary = db.Column(db.Numeric(10, 2))
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Leave Information
    annual_leave_balance = db.Column(db.Integer, default=21)  # days
    sick_leave_balance = db.Column(db.Integer, default=10)   # days
    personal_leave_balance = db.Column(db.Integer, default=3) # days
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    passport_record = db.relationship('PassportRecord', backref='employee')
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy='dynamic')
    subordinates = db.relationship('Employee', backref=db.backref('manager', remote_side=[id]))
    
    def __repr__(self):
        return f'<Employee {self.employee_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'email': self.email,
            'department': self.department,
            'position': self.position,
            'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
            'salary': float(self.salary) if self.salary else None,
            'annual_leave_balance': self.annual_leave_balance,
            'sick_leave_balance': self.sick_leave_balance,
            'personal_leave_balance': self.personal_leave_balance,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    
    # Leave Details
    leave_type = db.Column(db.String(50), nullable=False)  # annual, sick, personal, maternity, etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    
    # Approval Workflow
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    manager_approval = db.Column(db.String(20))  # approved, rejected, pending
    hr_approval = db.Column(db.String(20))      # approved, rejected, pending
    
    # AI Analysis
    ai_recommendation = db.Column(db.String(20))  # approve, reject, conditional, manual_review
    ai_confidence = db.Column(db.Float)
    ai_analysis = db.Column(db.Text)  # JSON string of AI analysis
    
    # Comments and History
    manager_comments = db.Column(db.Text)
    hr_comments = db.Column(db.Text)
    employee_comments = db.Column(db.Text)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    manager_reviewed_at = db.Column(db.DateTime)
    hr_reviewed_at = db.Column(db.DateTime)
    final_decision_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<LeaveRequest {self.id} - {self.employee.employee_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'days_requested': self.days_requested,
            'reason': self.reason,
            'status': self.status,
            'manager_approval': self.manager_approval,
            'hr_approval': self.hr_approval,
            'ai_recommendation': self.ai_recommendation,
            'ai_confidence': self.ai_confidence,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class HRQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    
    # Query Details
    subject = db.Column(db.String(200), nullable=False)
    query_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # leave, payroll, benefits, policy, other
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Contact Information (for external queries)
    contact_email = db.Column(db.String(120))
    contact_name = db.Column(db.String(100))
    
    # Response and Status
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    ai_response = db.Column(db.Text)
    hr_response = db.Column(db.Text)
    auto_resolved = db.Column(db.Boolean, default=False)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HRQuery {self.id} - {self.subject}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'subject': self.subject,
            'query_text': self.query_text,
            'category': self.category,
            'priority': self.priority,
            'contact_email': self.contact_email,
            'contact_name': self.contact_name,
            'status': self.status,
            'ai_response': self.ai_response,
            'hr_response': self.hr_response,
            'auto_resolved': self.auto_resolved,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class JobOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passport_record_id = db.Column(db.Integer, db.ForeignKey('passport_record.id'), nullable=False)
    
    # Position Details
    position_title = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    salary_offered = db.Column(db.Numeric(10, 2))
    start_date = db.Column(db.Date)
    employment_type = db.Column(db.String(50))  # full-time, part-time, contract
    
    # Offer Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, accepted, rejected, expired
    offer_sent_at = db.Column(db.DateTime)
    response_deadline = db.Column(db.Date)
    candidate_response = db.Column(db.String(20))  # accepted, rejected, negotiating
    
    # Email and Communication
    candidate_email = db.Column(db.String(120))
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    
    # Generated Content
    offer_letter_content = db.Column(db.Text)
    ai_generated = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    passport_record = db.relationship('PassportRecord', backref='job_offers')
    
    def __repr__(self):
        return f'<JobOffer {self.id} - {self.position_title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'passport_record_id': self.passport_record_id,
            'position_title': self.position_title,
            'department': self.department,
            'salary_offered': float(self.salary_offered) if self.salary_offered else None,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'employment_type': self.employment_type,
            'status': self.status,
            'candidate_email': self.candidate_email,
            'email_sent': self.email_sent,
            'ai_generated': self.ai_generated,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }