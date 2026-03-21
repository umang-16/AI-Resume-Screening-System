# pyre-ignore-all-errors
import os
from flask import Flask, render_template, redirect, url_for # pyre-ignore
from config import Config # pyre-ignore
from extensions import db, login_manager # pyre-ignore
from models import User # pyre-ignore

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp # pyre-ignore
    from routes.hr import hr_bp # pyre-ignore
    from routes.student import student_bp # pyre-ignore

    app.register_blueprint(auth_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(student_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    # Create upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5005)
