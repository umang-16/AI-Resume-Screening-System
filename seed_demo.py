from app import create_app # pyre-ignore
from extensions import db # pyre-ignore
from models import User, Job # pyre-ignore
from werkzeug.security import generate_password_hash # pyre-ignore

app = create_app()
with app.app_context():
    # 1. Create Demo HR
    hr = User.query.filter_by(email='hr@demo.com').first()
    if not hr:
        hr = User(
            name='TechCorp HR', 
            email='hr@demo.com', 
            password_hash=generate_password_hash('demo123', method='scrypt'), 
            role='hr'
        )
        db.session.add(hr)
        db.session.flush() # to get hr.id
        
        # Add a demo job posted by this HR
        job = Job(
            title='Junior Python Developer',
            description='Looking for an enthusiastic Python developer to build web applications.',
            required_skills='python, flask, sql, git',
            salary='$60k - $80k',
            experience='0-2 Years',
            location='Remote',
            hr_id=hr.id
        )
        db.session.add(job)
        
    # 2. Create Demo Student
    student = User.query.filter_by(email='student@demo.com').first()
    if not student:
        student = User(
            name='Alice Smith', 
            email='student@demo.com', 
            password_hash=generate_password_hash('demo123', method='scrypt'), 
            role='student', 
            education='B.Sc. in Computer Science', 
            skills='python, linux, github'
        )
        db.session.add(student)
        
    db.session.commit()
    print("Demo users and initial data created successfully!")
