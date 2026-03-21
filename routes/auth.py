# pyre-ignore-all-errors
from flask import Blueprint, render_template, redirect, url_for, request, flash # pyre-ignore
from flask_login import login_user, logout_user, login_required, current_user # pyre-ignore
from werkzeug.security import generate_password_hash, check_password_hash # pyre-ignore
from models import User, Notification # pyre-ignore
from extensions import db # pyre-ignore

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'hr':
            return redirect(url_for('hr.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'hr':
                return redirect(url_for('hr.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Please check your login details and try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role') # 'hr' or 'student'

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(
            email=email, 
            name=name, 
            password_hash=generate_password_hash(password, method='scrypt'), 
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth_bp.route('/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    for notif in current_user.notifications:
        notif.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for('index'))
