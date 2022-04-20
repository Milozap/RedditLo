from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    """Login Form"""

    username = StringField(
        "Username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(min=8, max=60)]
    )


class SignUpForm(FlaskForm):
    """Signup/Register form"""

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
