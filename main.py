from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "GHRAGSNJBNBFUREVH863"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pythonsqlite.db"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(60))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=60)]
    )


class SignUpForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)],
    )
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=60)]
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        new_user = User(
            email=form.email.data, username=form.username.data, password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("sign_up.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for("my_profile"))
        return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/my_profile")
@login_required
def my_profile():
    return render_template("my_profile.html", user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
