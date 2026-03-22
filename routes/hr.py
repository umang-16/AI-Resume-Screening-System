# pyre-ignore-all-errors
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory # pyre-ignore
from flask_login import login_required, current_user # pyre-ignore
from models import Job, Application, User, Notification # pyre-ignore
from extensions import db # pyre-ignore
from functools import wraps

hr_bp = Blueprint('hr', __name__, url_prefix='/hr')

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'hr':
            flash('You do not have permission to access that page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@hr_bp.route('/resume/<filename>')
@hr_required
def view_resume(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@hr_bp.route('/dashboard')
@hr_required
def dashboard():
    total_jobs = Job.query.filter_by(hr_id=current_user.id).count()
    jobs = Job.query.filter_by(hr_id=current_user.id).all()
    job_ids = [j.id for j in jobs]
    total_applicants = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    shortlisted = Application.query.filter(Application.job_id.in_(job_ids), Application.status == 'Shortlisted').count() if job_ids else 0
    
    # Advanced metrics
    recent_apps = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).limit(5).all() if job_ids else []
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    
    return render_template('hr/dashboard.html', total_jobs=total_jobs, total_applicants=total_applicants, shortlisted=shortlisted, recent_apps=recent_apps, notifications=notifications)

@hr_bp.route('/jobs', methods=['GET', 'POST'])
@hr_required
def manage_jobs():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills')
        salary = request.form.get('salary')
        experience = request.form.get('experience')
        location = request.form.get('location')
        
        new_job = Job(title=title, description=description, required_skills=required_skills, 
                      salary=salary, experience=experience, location=location, hr_id=current_user.id)
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('hr.manage_jobs'))
        
    jobs = Job.query.filter_by(hr_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template('hr/jobs.html', jobs=jobs)

@hr_bp.route('/job/<int:job_id>/delete', methods=['POST'])
@hr_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.hr_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('hr.manage_jobs'))
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted!', 'info')
    return redirect(url_for('hr.manage_jobs'))

@hr_bp.route('/job/<int:job_id>/candidates')
@hr_required
def view_candidates(job_id):
    job = Job.query.get_or_404(job_id)
    if job.hr_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('hr.manage_jobs'))
        
    applications = Application.query.filter_by(job_id=job.id).order_by(Application.match_score.desc()).all()
    return render_template('hr/candidates.html', job=job, applications=applications)

@hr_bp.route('/application/<int:app_id>/status/<string:status>')
@hr_required
def change_status(app_id, status):
    application = Application.query.get_or_404(app_id)
    if application.job.hr_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('hr.dashboard'))
        
    if status in ['Shortlisted', 'Rejected', 'Pending']:
        application.status = status
        notif = Notification(user_id=application.student_id, message=f'Your application for {application.job.title} was marked as {status}')
        db.session.add(notif)
        db.session.commit()
        flash(f'Application status updated to {status}', 'success')
        
    return redirect(url_for('hr.view_candidates', job_id=application.job_id))

@hr_bp.route('/profile', methods=['GET', 'POST'])
@hr_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.company_name = request.form.get('company_name', current_user.company_name)
        current_user.company_details = request.form.get('company_details', current_user.company_details)
        db.session.commit()
        flash('HR Profile and Company Details updated successfully!', 'success')
        return redirect(url_for('hr.profile'))
    return render_template('hr/profile.html')

@hr_bp.route('/schedule_interview/<int:app_id>', methods=['POST'])
@hr_required
def schedule_interview(app_id):
    application = Application.query.get_or_404(app_id)
    if application.job.hr_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('hr.dashboard'))
        
    date_str = request.form.get('interview_date')
    interview_type = request.form.get('interview_type')
    interview_location = request.form.get('interview_location')
    
    if date_str:
        from datetime import datetime # pyre-ignore
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            application.interview_date = dt
            application.interview_type = interview_type
            application.interview_location = interview_location
            application.status = 'Interview Scheduled'
            
            notif = Notification(user_id=application.student_id, message=f'An {interview_type} interview has been scheduled for {application.job.title} on {dt.strftime("%b %d, %Y at %I:%M %p")}')
            db.session.add(notif)
            db.session.commit()
            flash('Interview scheduled successfully!', 'success')
        except ValueError:
            flash('Invalid date format provided.', 'danger')
            
    return redirect(url_for('hr.view_candidates', job_id=application.job_id))

import os # pyre-ignore
from werkzeug.utils import secure_filename # pyre-ignore

@hr_bp.route('/upload_offer/<int:app_id>', methods=['POST'])
@hr_required
def upload_offer(app_id):
    application = Application.query.get_or_404(app_id)
    if application.job.hr_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('hr.dashboard'))
        
    if 'offer_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('hr.view_candidates', job_id=application.job_id))
        
    file = request.files['offer_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('hr.view_candidates', job_id=application.job_id))
        
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(f"offer_{application.id}_{file.filename}")
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) # pyre-ignore
        
        application.offer_letter_filename = filename
        application.status = 'Offered'
        
        notif = Notification(user_id=application.student_id, message=f'Congratulations! You have received an Offer Letter for {application.job.title}!')
        db.session.add(notif)
        db.session.commit()
        flash('Offer letter dispatched successfully!', 'success')
    else:
        flash('Only PDF files are allowed for offer letters.', 'warning')
        
    return redirect(url_for('hr.view_candidates', job_id=application.job_id))

@hr_bp.route('/application/<int:app_id>/analysis')
@hr_required
def application_analysis(app_id):
    application = Application.query.get_or_404(app_id)
    if application.job.hr_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('hr.dashboard'))
        
    req_skills = set(s.strip().lower() for s in application.job.required_skills.split(',') if s.strip())
    res_skills = set(s.strip().lower() for s in (application.student.skills or '').split(',') if s.strip())
    
    missing_skills = list(req_skills - res_skills)
    matched_skills = list(req_skills & res_skills)
    extra_skills = list(res_skills - req_skills)
    
    return render_template('hr/resume_analysis.html', app=application, missing_skills=missing_skills, matched_skills=matched_skills, extra_skills=extra_skills)

@hr_bp.route('/application/<int:app_id>/download_analysis')
@hr_required
def download_analysis(app_id):
    import csv # pyre-ignore
    import io # pyre-ignore
    from flask import Response # pyre-ignore
    
    application = Application.query.get_or_404(app_id)
    if application.job.hr_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('hr.dashboard'))
        
    req_skills = set(s.strip().lower() for s in application.job.required_skills.split(',') if s.strip())
    res_skills = set(s.strip().lower() for s in (application.student.skills or '').split(',') if s.strip())
    
    missing_skills = list(req_skills - res_skills)
    matched_skills = list(req_skills & res_skills)
    extra_skills = list(res_skills - req_skills)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Meta Data
    writer.writerow(['Candidate Name', application.student.name])
    writer.writerow(['Job Applied For', application.job.title])
    writer.writerow(['AI Match Score', f"{application.match_score}%"])
    writer.writerow(['Application Date', application.applied_at.strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Main Categorizations Column
    writer.writerow(['CATEGORY (CRITERIA)', 'SKILL'])
    
    if matched_skills:
        for skill in matched_skills:
            writer.writerow(['VERIFIED CORE COMPETENCY (MATCH)', skill.title()])
    else:
        writer.writerow(['VERIFIED CORE COMPETENCY (MATCH)', 'None detected'])
        
    if missing_skills:
        for skill in missing_skills:
            writer.writerow(['MISSING PREREQUISITE (MISSGING)', skill.title()])
    else:
        writer.writerow(['MISSING PREREQUISITE (MISSING)', 'None. Perfect Match!'])
        
    if extra_skills:
        for skill in extra_skills:
            writer.writerow(['SURROUNDING TECH (EXTRA/BONUS)', skill.title()])
    else:
        writer.writerow(['SURROUNDING TECH (EXTRA/BONUS)', 'None detected'])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=Candidate_Analysis_{application.student.name.replace(' ', '_')}.csv"}
    )
