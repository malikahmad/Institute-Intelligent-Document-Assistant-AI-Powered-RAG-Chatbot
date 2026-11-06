import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import User

bp = Blueprint("auth", __name__)

def valid_email(email):
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email or ""))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        error = None
        if not name or len(name) > 120: error = "Enter a name between 1 and 120 characters."
        elif not valid_email(email): error = "Enter a valid email address."
        elif len(password) < 8: error = "Password must contain at least 8 characters."
        elif password != confirm: error = "Passwords do not match."
        elif db.session.scalar(select(User).where(User.email == email)): error = "That email is already registered."
        if error:
            flash(error, "danger")
        else:
            try:
                user = User(name=name, email=email, role="student")
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("Account created. Please sign in.", "success")
                return redirect(url_for("auth.login"))
            except IntegrityError:
                db.session.rollback()
                flash("That email is already registered.", "danger")
            except Exception:
                db.session.rollback()
                current_app.logger.exception("Registration failed")
                flash("Registration failed. Please try again.", "danger")
    return render_template("register.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.session.scalar(select(User).where(User.email == email))
        if user and user.active and user.check_password(password):
            login_user(user, remember=True)
            nxt = request.args.get("next", "")
            if nxt.startswith("/") and not nxt.startswith("//"): return redirect(nxt)
            return redirect(url_for("main.dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have signed out.", "success")
    return redirect(url_for("auth.login"))
