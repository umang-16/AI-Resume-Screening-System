# pyre-ignore-all-errors
from extensions import db # pyre-ignore
from flask_login import UserMixin # pyre-ignore
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'hr' or 'student'
    phone = db.Column(db.String(20), nullable=True)
    
    # Student specific
    education = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    resume_filename = db.Column(db.String(200), nullable=True)
    
    # HR specific
    company_name = db.Column(db.String(150), nullable=True)
    company_details = db.Column(db.Text, nullable=True)
    
    applications = db.relationship('Application', backref='student', lazy=True)
    jobs_posted = db.relationship('Job', backref='hr', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, order_by='Notification.created_at.desc()', cascade="all, delete-orphan")

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(50), nullable=True)
    experience = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('Application', backref='job', lazy=True, cascade="all, delete-orphan")

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending') # Pending, Shortlisted, Rejected, Interview Scheduled, Offered
    match_score = db.Column(db.Float, default=0.0)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New lifecycle attributes
    interview_date = db.Column(db.DateTime, nullable=True)
    interview_type = db.Column(db.String(50), nullable=True) # Online, In-Person
    interview_location = db.Column(db.String(200), nullable=True) # Link or Address
    offer_letter_filename = db.Column(db.String(200), nullable=True)
