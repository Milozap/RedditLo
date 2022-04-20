from flask import Flask
from flask_login import LoginManager

from .api.models import db, User
from .api.routes import api
from .frontend.routes import frontend


def create_app():
    app = Flask("__name__")
    app.register_blueprint(api)
    app.register_blueprint(frontend)
    app.config["SECRET_KEY"] = "GHRAGSNJBNBFUREVH863"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pythonsqlite.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "frontend.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
