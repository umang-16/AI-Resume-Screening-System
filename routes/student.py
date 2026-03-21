# pyre-ignore-all-errors
import os
from werkzeug.utils import secure_filename # pyre-ignore
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory # pyre-ignore
from flask_login import login_required, current_user # pyre-ignore
from models import Job, Application, User, Notification # pyre-ignore
from extensions import db # pyre-ignore
from utils.ai_parser import extract_text_from_pdf, extract_skills_from_text, match_skills # pyre-ignore
from functools import wraps

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('You do not have permission to access that page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@student_bp.route('/dashboard')
@student_required
def dashboard():
    applications = Application.query.filter_by(student_id=current_user.id).order_by(Application.applied_at.desc()).all()
    return render_template('student/dashboard.html', applications=applications)

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.education = request.form.get('education', current_user.education)
        
        file = request.files.get('resume')
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            current_user.resume_filename = filename
            
            # Extract skills via AI
            text = extract_text_from_pdf(filepath)
            skills = extract_skills_from_text(text)
            current_user.skills = skills
            flash('Profile and Resume updated successfully. Skills extracted!', 'success')
        else:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            
        db.session.commit()
        return redirect(url_for('student.profile'))
        
    return render_template('student/profile.html')

@student_bp.route('/jobs')
@student_required
def list_jobs():
    search = request.args.get('search', '')
    if search:
        jobs = Job.query.filter(Job.title.ilike(f'%{search}%') | Job.required_skills.ilike(f'%{search}%')).all()
    else:
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        
    applied_jobs = [app.job_id for app in current_user.applications]
    return render_template('student/jobs.html', jobs=jobs, applied_jobs=applied_jobs)

@student_bp.route('/apply/<int:job_id>', methods=['POST'])
@student_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    if not current_user.resume_filename:
        flash('Please upload your resume in the profile section before applying.', 'warning')
        return redirect(url_for('student.profile'))
        
    existing_app = Application.query.filter_by(student_id=current_user.id, job_id=job.id).first()
    if existing_app:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('student.list_jobs'))
        
    # Calculate initial match score based on AI extracted skills
    score = match_skills(current_user.skills, job.required_skills)
    
    new_app = Application(student_id=current_user.id, job_id=job.id, match_score=score)
    db.session.add(new_app)
    
    notif = Notification(user_id=job.hr_id, message=f'New application from {current_user.name} for {job.title}')
    db.session.add(notif)
    
    db.session.commit()
    
    flash(f'Successfully applied for {job.title}!', 'success')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/resume/<filename>')
@student_required
def view_resume(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
@student_bp.route('/job/<int:job_id>')
@student_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    existing_app = None
    missing_skills = []
    
    if current_user.is_authenticated:
        existing_app = Application.query.filter_by(student_id=current_user.id, job_id=job.id).first()
        
        # Calculate missing skills
        req_skills = set([s.strip().lower() for s in job.required_skills.split(',') if s.strip()])
        res_skills = set()
        if current_user.skills:
            res_skills = set([s.strip().lower() for s in current_user.skills.split(',') if s.strip()])
            
        missing_skills = list(req_skills - res_skills)
        
    return render_template('student/job_detail.html', job=job, existing_app=existing_app, missing_skills=missing_skills)

@student_bp.route('/withdraw/<int:job_id>', methods=['POST'])
@student_required
def withdraw_application(job_id):
    app = Application.query.filter_by(student_id=current_user.id, job_id=job_id).first()
    if app:
        db.session.delete(app)
        db.session.commit()
        flash('Application withdrawn successfully.', 'info')
    else:
        flash('Application not found.', 'danger')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/offer/<filename>')
@student_required
def view_offer(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename) # pyre-ignore
