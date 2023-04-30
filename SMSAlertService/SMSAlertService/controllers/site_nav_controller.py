from flask import Blueprint, render_template, session
from SMSAlertService import app
from SMSAlertService.decorators import protected

site_nav_bp = Blueprint('site_nav_controller', __name__)


@site_nav_bp.route("/", methods=["GET"])
def home():
    return render_template('home.html')


@site_nav_bp.route("/login", methods=["GET"])
def login():
    if 'login_attempts' not in session:
        session['login_attempts'] = 0
    return render_template('login.html')


@site_nav_bp.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template('signup.html')


@site_nav_bp.route("/support", methods=["GET"])
def support():
    return render_template('support.html')


@site_nav_bp.route("/privacy", methods=["GET"])
def privacy():
    return render_template('privacy.html')


@site_nav_bp.route("/instructions", methods=["GET"])
def instructions():
    return render_template('instructions.html')


