from .models import User, Post, db
from ..frontend.forms import SignUpForm, AddPostForm
from flask import Blueprint, jsonify
from flask_login import login_required
from werkzeug.security import generate_password_hash

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/users/all")
@login_required
def get_all_users():
    """Route that returns all users from DB"""
    users = User.query.all()
    return jsonify(users)


@api.route("/users/<username>")
def get_user(username):
    """Route that returns user if they exist"""
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify(user), 200
    else:
        return {}, 204


@api.route("/users/add_user", methods=["POST"])
def add_user(data=None):
    """Route to validate user data and add user"""
    form = SignUpForm()

    # check if there is data in request
    if data:
        form = data

    # return error if some data is missing
    if not form.username.data or not form.email.data or not form.password.data:
        return (
            jsonify({"status": "error", "message": "Missing data"}),
            400,
        )
    # return error if user with same username already exists
    if User.query.filter_by(username=form.username.data).first():
        return (
            jsonify(
                {"status": "error", "message": "User with that username already exists"}
            ),
            409,
        )
    # return error if user with same email already exists
    if User.query.filter_by(email=form.email.data).first():
        return (
            jsonify(
                {"status": "error", "message": "User with that email already exists"}
            ),
            409,
        )

    # create new user and save them in DB
    hashed_password = generate_password_hash(form.password.data, method="sha256")
    new_user = User(
        email=form.email.data, username=form.username.data, password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return (
        jsonify({"status": "success", "message": "User added successfully"}),
        200,
    )


@api.route("/users/delete_user/<username>")
def delete_user(username):
    """Route that deletes user if they exist"""
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return (
            jsonify({"status": "success", "message": "User deleted successfully"}),
            200,
        )
    else:
        return (
            jsonify({"status": "error", "message": "User doesn't exist"}),
            404,
        )


@api.route("/posts/all")
def get_all_posts():
    """Route that returns all posts from DB"""
    posts = Post.query.all()
    return jsonify(posts)


@api.route("/posts/create_post", methods=["POST"])
def create_post(data=None, user_id=None):
    """Route to validate post data and add user"""
    form = AddPostForm()

    # check if there is data in request
    if data:
        form = data

    # return error if text data is missing
    if not form.text.data:
        return (
            jsonify({"status": "error", "message": "Post text cannot be empty"}),
            400,
        )
    if not user_id and not form.author.data:
        return (
            jsonify({"status": "error", "message": "User id missing"}),
            400,
        )
    if user_id:
        new_post = Post(text=form.text.data, author=user_id)
    if form.author.data:
        new_post = Post(text=form.text.data, author=form.author.data)
    db.session.add(new_post)
    db.session.commit()

    return (
        jsonify({"status": "success", "message": "Post added successfully"}),
        200,
    )
