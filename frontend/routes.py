import json
from ..api.models import User
from ..api.routes import add_user
from .forms import LoginForm, SignUpForm
from flask import render_template, redirect, url_for, request, Blueprint, flash
from werkzeug.security import check_password_hash
from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user,
)

frontend = Blueprint(
    "frontend",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/frontend/static",
)


@frontend.route("/")
def index():
    """home page"""
    return render_template("index.html", user=current_user)


@frontend.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """Signup/Register route"""

    # break glass in case of emergency
    # print(request.data, file=sys.stderr)
    form = SignUpForm()
    if request.method == "POST":

        # return error if form data is missing
        if not form.username.data or not form.email.data or not form.password.data:
            return redirect(url_for("frontend.sign_up")), 400
        if form.validate_on_submit():
            # try to add user and process response from api
            r = add_user(data=form)
            response = json.loads(r[0].response[0])
            status_code = r[1]
            # print(json.loads(r[0].response[0]), file=sys.stderr)

            # return 409 and error message on error
            if status_code != 200:
                flash(response["message"], "error")
                return redirect(url_for("frontend.sign_up")), 409

            # redirect to login if everything went well
            return redirect(url_for("frontend.login"))
    return render_template("sign_up.html", user=current_user, form=form)


@frontend.route("/login", methods=["GET", "POST"])
def login():
    """Login route"""
    form = LoginForm()
    if request.method == "POST":
        # return error if form data is missing
        if not form.username.data or not form.password.data:
            return redirect(url_for("frontend.login")), 400

        if form.validate_on_submit():
            # TODO change that to get_user from api
            # user = get_user(username=form.username.data)

            user = User.query.filter_by(username=form.username.data).first()
            # check if user exists in DB
            if user:
                # check if password matches
                if check_password_hash(user.password, form.password.data):
                    # login and redirect to my_profile if everything went well
                    login_user(user, remember=True)
                    return redirect(url_for("frontend.my_profile"))
                else:
                    # return 409 and error message on invalid password
                    flash("Invalid password provided", "error")
                    redirect(url_for("frontend.login")), 409
            else:
                # return 409 and error message if user doesn't exist
                flash("User doesn't exist", "error")
                redirect(url_for("frontend.login")), 409

        # return 409 and error message on for validation error
        return redirect(url_for("frontend.login")), 409

    return render_template("login.html", user=current_user, form=form)


@frontend.route("/my_profile")
@login_required
def my_profile():
    return render_template("my_profile.html", user=current_user)


@frontend.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("frontend.index"))
