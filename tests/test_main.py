from .. import create_app, db, User
import pytest
import json
from flask_login import current_user
from werkzeug.security import generate_password_hash


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


def test_sign_up_with_invalid_user(client):
    response = client.post(
        "/sign_up",
        data=json.dumps({"username": "", "password": "", "email": ""}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 409
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


def test_my_profile_redirects_not_logged_in_user(client):
    response = client.get("/my_profile")
    assert response.status_code == 302
    assert response.location == "/login?next=%2Fmy_profile"


def test_login_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_invalid_data(client):
    response = client.post(
        "/login",
        data=json.dumps({"username": "", "password": ""}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 409
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


def test_logout_redirects(client):
    response = client.get("/logout")
    assert response.status_code == 302
