from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GHRAGSNJBNBFUREVH863'

class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = StringField(
        "Password", validators=[InputRequired(), Length(min=8, max=60)]
    )

class SignUpForm(FlaskForm):
	email = StringField(
		"Email", validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)]
	)
	username = StringField(
        "Username", validators=[InputRequired(), Length(min=4, max=15)])
	password = StringField(
        "Password", validators=[InputRequired(), Length(min=8, max=60)]
    )

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
	form = SignUpForm()

	if form.validate_on_submit():
		return f'<h1>Email: {form.email.data} Username: {form.username.data} Password: {form.password.data}'
	
	return render_template("signup.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
    	return f'<h1>Username: {form.username.data} Password: {form.password.data}'

    return render_template("login.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
