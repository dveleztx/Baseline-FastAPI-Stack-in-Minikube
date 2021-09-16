# Imports
import json
# Custom Imports
from example_com.infrastructure.jwt_token_auth import set_token
from example_com.models.validation import ValidationError


###############################################################################
# Create Test Account
###############################################################################
def test_account_successful_registration(test_app_with_db):
    new_user = {
        "first_name": "Pytester",
        "last_name": "McPythonson",
        "username": "pytest",
        "email": "pytest@example.com",
        "password": "fixtuREz2p@ss"
    }
    response = test_app_with_db.post("/api/account/register", data=json.dumps(new_user))

    assert response.status_code == 201


###############################################################################
# Test GET Requests
###############################################################################
def test_account_unauthenticated(test_app_with_db):
    response = test_app_with_db.get("/api/account")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_account_invalid_token(test_app_with_db):
    headers = {
        "Authorization": "Bearer madeuptoken"
    }
    try:
        response = test_app_with_db.get("/api/account", headers=headers)

        assert response.status_code == 401
        assert response.content.decode("utf-8") == "Invalid token"
    except ValidationError as ve:
        assert ve.error_msg == "Invalid token"


def test_account_authentication_token(test_app_with_db):
    token = set_token("pytest")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = test_app_with_db.get("/api/account", headers=headers)

    assert response.status_code == 200


###############################################################################
# Test POST Requests
###############################################################################
def test_account_incorrect_user(test_app_with_db):
    creds = {
        "username": "xyz",
        "password": "nonexistent"
    }
    response = test_app_with_db.post("/api/token", data=creds)

    assert response.status_code == 400
    assert response.content.decode("utf-8") == "Incorrect username or password"


def test_account_correct_user(test_app_with_db):
    creds = {
        "username": "pytest",
        "password": "fixtuREz2p@ss"
    }
    response = test_app_with_db.post("/api/token", data=creds)

    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"


# Test Account Creation Restraints
def test_first_name_restraint(test_app_with_db):
    new_user = {
        "first_name": "",
        "last_name": "lillast",
        "username": "liltest",
        "email": "liltest@example.com",
        "password": "testlilpass"
    }
    response = test_app_with_db.post("/api/account/register", data=json.dumps(new_user))

    assert response.status_code == 422
    for details_key in response.json()["detail"]:
        assert details_key["msg"] == "ensure this value has at least 1 characters"


def test_last_name_restraint(test_app_with_db):
    new_user = {
        "first_name": "lilfirst",
        "last_name": "",
        "username": "liltest",
        "email": "liltest@example.com",
        "password": "testlilpass"
    }
    response = test_app_with_db.post("/api/account/register", data=json.dumps(new_user))
    for details_key in response.json()["detail"]:
        assert details_key["msg"] == "ensure this value has at least 1 characters"

    assert response.status_code == 422


def test_username_restraint(test_app_with_db):
    new_user = {
        "first_name": "lilfirst",
        "last_name": "lillast",
        "username": "lil",
        "email": "liltest@example.com",
        "password": "testlilpass"
    }
    response = test_app_with_db.post("/api/account/register", data=json.dumps(new_user))

    assert response.status_code == 422
    for details_key in response.json()["detail"]:
        assert details_key["msg"] == "ensure this value has at least 4 characters"


def test_password_restraint(test_app_with_db):
    new_user = {
        "first_name": "lilfirst",
        "last_name": "lillast",
        "username": "liltest",
        "email": "liltest@example.com",
        "password": "toolittle"
    }
    response = test_app_with_db.post("/api/account/register", data=json.dumps(new_user))

    assert response.status_code == 422
    for details_key in response.json()["detail"]:
        assert details_key["msg"] == "ensure this value has at least 10 characters"


###############################################################################
# Test PUT Requests
###############################################################################
def test_account_update_info(test_app_with_db):
    token = set_token("pytest")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    updated_user_info = {
        "first_name": "ChangePytester",
        "last_name": "ChangePythonson"
    }

    response = test_app_with_db.put("/api/account/pytest", data=json.dumps(updated_user_info), headers=headers)

    assert response.status_code == 200


def test_account_update_password(test_app_with_db):
    token = set_token("pytest")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    old_new_pass = {
        "old_password": "fixtuREz2p@ss",
        "new_password": "icantTH!NKof1g00d1"
    }
    response = test_app_with_db.put("/api/account/pytest/security", data=json.dumps(old_new_pass), headers=headers)

    assert response.status_code == 200


###############################################################################
# Test New Password
###############################################################################
def test_account_updated_password(test_app_with_db):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    new_creds = {
        "username": "pytest",
        "password": "icantTH!NKof1g00d1"
    }
    response = test_app_with_db.post("/api/token", data=new_creds, headers=headers)

    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"


###############################################################################
# Test DELETE Requests
###############################################################################
def test_account_deletion(test_app_with_db):
    token = set_token("pytest")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = test_app_with_db.delete("/api/account/pytest", headers=headers)

    assert response.status_code == 204
