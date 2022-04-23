from .. import create_app, db, User
import pytest
import json
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash


@pytest.fixture(scope="module")
def valid_user_raw_password():
    return "testuserpassword"


@pytest.fixture(scope="module")
def valid_user(valid_user_raw_password):
    user = User(
        email="test@test.com",
        username="TestUser",
        password=generate_password_hash(valid_user_raw_password, method="sha256"),
    )
    return user


@pytest.fixture()
def test_with_authenticated_user(app):
    @login_manager.request_loader
    def load_user_from_request(request):
        return User.query.first()


@pytest.fixture(scope="module")
def app():
    app = create_app()
    with app.app_context():
        app.config["TESTING"] = True
        app.config["CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + "test.db"
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["LOGIN_DISABLED"] = True
        db.init_app(app)
        db.create_all()

        yield app
    with app.app_context():
        db.session.remove()
        db.close_all_sessions()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


print("Test api:")


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


def test_sign_up_loads(client):
    response = client.get("/sign_up")
    assert response.status_code == 200


def test_sign_up_with_empty_user(client):
    response = client.post(
        "/sign_up",
        data=json.dumps({"username": "", "password": "", "email": ""}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.location == "/sign_up"


def test_sign_up_with_valid_user(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/sign_up",
        data=json.dumps(
            {
                "username": valid_user.username,
                "password": valid_user_raw_password,
                "email": valid_user.email,
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 302
    assert response.location == "/login"


def test_sign_up_with_duplicate_username(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/sign_up",
        data=json.dumps(
            {
                "username": valid_user.username,
                "password": valid_user_raw_password,
                "email": "test2@test.pl",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 409
    assert response.location == "/sign_up"


def test_sign_up_with_duplicate_email(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/sign_up",
        data=json.dumps(
            {
                "username": "TestUser2",
                "password": valid_user_raw_password,
                "email": valid_user.email,
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 409
    assert response.location == "/sign_up"


"""
def test_my_profile_redirects_not_logged_in_user(client):
    response = client.get("/my_profile")
    assert response.status_code == 302
    assert response.location == "/login?next=%2Fmy_profile"
"""


def test_login_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_empty_data(client):
    response = client.post(
        "/login",
        data=json.dumps({"username": "", "password": ""}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.location == "/login"


def test_login_not_existing_user(client):
    response = client.post(
        "/login",
        data=json.dumps({"username": "TestLogin", "password": "testloginpassword"}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 409
    assert response.location == "/login"


def test_login_existing_user_wrong_password(
    client, valid_user, valid_user_raw_password
):
    response = client.post(
        "/login",
        data=json.dumps(
            {"username": valid_user.username, "password": "invalidpassword"}
        ),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 409
    assert response.location == "/login"


def test_login_existing_user(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/login",
        data=json.dumps(
            {"username": valid_user.username, "password": valid_user_raw_password}
        ),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 302
    assert response.location == "/my_profile"


def test_my_profile_loads_for_logged_user(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/login",
        data=json.dumps(
            {"username": valid_user.username, "password": valid_user_raw_password}
        ),
        headers={"Content-Type": "application/json"},
    )
    response = client.get("/my_profile")
    assert response.status_code == 200
    # TODO: check if logged in user is correct
    # assert client.current_user == "/login?next=%2Fmy_profile"


def test_user_api_get_one(client, valid_user, valid_user_raw_password):

    response = client.get("/api/users/" + valid_user.username)
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert data["email"] == valid_user.email
    assert data["username"] == valid_user.username
    check_password_hash(data["password"], valid_user_raw_password) == True


def test_user_get_all(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/login",
        data=json.dumps(
            {"username": valid_user.username, "password": valid_user_raw_password}
        ),
        headers={"Content-Type": "application/json"},
    )

    response = client.get("/api/users/all")
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert len(data) == 1
    assert data[0]["email"] == valid_user.email
    assert data[0]["username"] == valid_user.username
    check_password_hash(data[0]["password"], valid_user_raw_password) == True


def test_user_api_add_user_with_empty_user(client):
    response = client.post(
        "/api/users/add_user",
        data=json.dumps({"username": "", "password": "", "email": ""}),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "Missing data"
    assert response.status_code == 400


def test_delete_returns_404_on_invalid_user(client):
    response = client.get("/api/users/delete_user/testdelete")
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "User doesn't exist"
    assert response.status_code == 404


def test_delete_returns_200_on_valid_user(client, valid_user):
    response = client.get("/api/users/delete_user/" + valid_user.username)
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "User deleted successfully"
    assert response.status_code == 200


def test_user_api_add_user_with_valid_user(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/api/users/add_user",
        data=json.dumps(
            {
                "username": valid_user.username,
                "password": valid_user_raw_password,
                "email": valid_user.email,
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "User added successfully"
    assert response.status_code == 200


def test_user_api_add_user_with_duplicate_username(
    client, valid_user, valid_user_raw_password
):
    response = client.post(
        "/api/users/add_user",
        data=json.dumps(
            {
                "username": valid_user.username,
                "password": valid_user_raw_password,
                "email": "test2@test.pl",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "User with that username already exists"
    assert response.status_code == 409


def test_user_api_add_user_with_duplicate_email(
    client, valid_user, valid_user_raw_password
):
    response = client.post(
        "/api/users/add_user",
        data=json.dumps(
            {
                "username": "TestUser2",
                "password": valid_user_raw_password,
                "email": valid_user.email,
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "User with that email already exists"
    assert response.status_code == 409


def test_user_api_get_all(client, valid_user, valid_user_raw_password):
    response = client.post(
        "/login",
        data=json.dumps(
            {"username": valid_user.username, "password": valid_user_raw_password}
        ),
        headers={"Content-Type": "application/json"},
    )

    response = client.get("/api/users/all")
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert len(data) == 1
    assert data[0]["email"] == valid_user.email
    assert data[0]["username"] == valid_user.username
    check_password_hash(data[0]["password"], valid_user_raw_password) == True


def test_post_api_get_returns_empty_list(client, valid_user, valid_user_raw_password):
    response = client.get("/api/posts/all")
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data == []


def test_post_api_create_empty_post_returns_400(
    client, valid_user, valid_user_raw_password
):
    response = client.post(
        "/api/posts/create_post",
        data=json.dumps({"text": "", "author": 1}),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "Post text cannot be empty"
    assert response.status_code == 400


def test_post_api_create_valid_post_returns_200(
    client, valid_user, valid_user_raw_password
):
    response = client.post(
        "/api/posts/create_post",
        data=json.dumps({"text": "Test Post", "author": 1}),
        headers={"Content-Type": "application/json"},
    )
    data = json.loads(response.get_data(as_text=True))
    assert data["message"] == "Post added successfully"
    assert response.status_code == 200


def test_post_api_get_returns_added_post(client, valid_user, valid_user_raw_password):
    response = client.get("/api/posts/all")
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data == [{"id": 1, "text": "Test Post"}]


def test_logout_redirects(client):
    response = client.get("/logout")
    assert response.status_code == 302
