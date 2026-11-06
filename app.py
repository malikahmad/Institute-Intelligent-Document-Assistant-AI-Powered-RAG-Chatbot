from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from sqlalchemy import select
from config import Config
from extensions import db, login_manager, csrf
from models import User
from auth import bp as auth_bp
from main import bp as main_bp
from routes.admin import bp as admin_bp
from routes.chat import bp as chat_bp
from routes.evaluation import bp as evaluation_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config: app.config.update(test_config)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try: return db.session.get(User, int(user_id))
        except (ValueError, TypeError): return None

    for blueprint in (auth_bp, main_bp, admin_bp, chat_bp, evaluation_bp):
        app.register_blueprint(blueprint)

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        app.logger.warning("CSRF validation failed: %s", error.description)
        return render_template("error.html", code=400,
            message="Your security token is invalid or expired. Refresh the page and try again."), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("error.html", code=403, message="You do not have permission to access this page."), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(413)
    def too_large(error):
        return render_template("error.html", code=413, message="The uploaded file is too large."), 413

    with app.app_context():
        app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
        app.config["VECTOR_FOLDER"].mkdir(parents=True, exist_ok=True)
        db.create_all()
        email, password = app.config["ADMIN_EMAIL"].strip().lower(), app.config["ADMIN_PASSWORD"]
        if email and password and not db.session.scalar(select(User).where(User.email == email)):
            admin = User(name=app.config["ADMIN_NAME"], email=email, role="admin")
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            app.logger.info("Bootstrap administrator created.")
    return app

app = create_app()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
