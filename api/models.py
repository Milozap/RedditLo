from datetime import datetime
from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


@dataclass
class User(UserMixin, db.Model):
    """User Model"""

    id: int
    username: str
    email: str
    password: str

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(60))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    posts = db.relationship("Post", backref="user", passive_deletes=True)


@dataclass
class Post(db.Model):
    id: int
    text: str

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    text = db.Column(db.Text, nullable=False)
    author = db.Column(
        db.Integer, db.ForeignKey("user.id", on_delete="CASCADE"), nullable=False
    )
