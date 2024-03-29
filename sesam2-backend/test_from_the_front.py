"""
Some basic testing of the API from the front-end perspective. This is not a
complete test suite and will never be.
prerequisites:
    - start a server reachable at http://localhost:8000
    - use a dev environment OR
        - have a user 'test' with password 'test'
        - have a admin user 'admin' with password 'admin'
        - have a legit door with id '001b823d-1f5c-4f39-9e74-015bb2dcef8f'

"""
import requests
from requests import Response
import jose
from jose import jwt
import pytest
from datetime import datetime, time, timedelta


INVALID_DOOR_ID = "0000000000000-1000-1000-000000000000"
VALID_DOOR_ID = "001b823d-1f5c-4f39-9e74-015bb2dcef8f"
APP_URL = "http://localhost:8000"

now = datetime.now()


def get_token(username: str, password: str) -> Response:
    # get the token from url
    url = f"{APP_URL}/token"
    return requests.post(url, json={'username': username, 'password': password})


def decode_token(token):
    return jwt.get_unverified_claims(token['access_token'])

def auth_header(token):
    return {
        'Authorization': f'Bearer {token.get("access_token")}',
        'Content-Type': 'application/json',
    }

@pytest.fixture
def normal_token():
    return get_token('test', 'test').json()

@pytest.fixture
def admin_token():
    return get_token('admin', 'admin').json()


def test_get_normal_token_and_decode():
    response = get_token('test', 'test')
    assert response.status_code == 200
    token = response.json()
    assert token.get('access_token')
    assert token.get('expires')
    decoded = decode_token(token)
    assert decoded.get('name') == 'test'
    assert not decoded.get('is_admin')


def test_get_admin_token_and_decode():
    response = get_token('admin', 'admin')
    assert response.status_code == 200
    token = response.json()
    assert token.get('access_token')
    assert token.get('expires')
    decoded = decode_token(token)
    assert decoded.get('name') == 'admin'
    assert decoded.get('is_admin')


def test_get_broken_token_and_decode():
    response = get_token('admin', 'h4ck')
    assert response.status_code == 401


def test_create_normal_user(admin_token):
    url = f"{APP_URL}/admin/create_user"
    response = requests.post(url, headers=auth_header(admin_token), json=dict(username='knut', password='knut'))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'

    registration_code = response.json().get('registration_code')
    assert registration_code

    url = f"{APP_URL}/register"
    response = requests.post(url, json=dict(username='knut', password='knut', registration_code=registration_code))
    assert response.status_code == 200


def test_get_token_of_created_user():
    response = get_token('knut', 'knut')
    assert response.status_code == 200
    token = response.json()
    assert token.get('access_token')
    assert token.get('expires')
    decoded = decode_token(token)
    assert decoded.get('name') == 'knut'
    assert not decoded.get('is_admin')


def test_create_user_by_normal_user_fails(normal_token):
    url = f"{APP_URL}/admin/create_user"
    response = requests.post(url, headers=auth_header(normal_token), json=dict(username='sue', password='sue'))
    assert response.status_code == 401


def test_update_user(admin_token):
    url = f"{APP_URL}/admin/update_user"
    response = requests.post(url, headers=auth_header(admin_token), json=dict(username='knut', is_admin=True))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'
    response = get_token('knut', 'knut')
    token = response.json()
    decoded = decode_token(token)
    assert decoded.get('is_admin') == True
    requests.post(url, headers=auth_header(admin_token), json=dict(username='knut', is_admin=True))


@pytest.mark.skip(reason="This is not implemented yet.")
def test_delete_user(admin_token):
    url = f"{APP_URL}/admin/create_user"
    requests.post(url, headers=auth_header(admin_token), json=dict(username='harribert', password='deleteme'))

    url = f"{APP_URL}/admin/delete_user"
    response = requests.post(url, headers=auth_header(admin_token), json=dict(username='harribert'))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


@pytest.mark.skip(reason="This is not implemented yet.")
def test_delete_user_by_normal_user_fails(normal_token):
    url = f"{APP_URL}/admin/delete_user"
    response = requests.post(url, headers=auth_header(normal_token), json=dict(username='test'))
    assert response.status_code == 401


def grant(*, username, door_id = VALID_DOOR_ID, weekday = now.isoweekday(), grant_start = now.hour - 1, grant_end = now.hour + 1):
    return dict(username=username, door_id=door_id, weekday=weekday, grant_start=grant_start, grant_end=grant_end)



@pytest.mark.skip(reason="This is not implemented yet.")
def test_add_grant(admin_token):
    url = f"{APP_URL}/admin/add_grant"
    grant = grant(username='knut')
    response = requests.post(url, headers=auth_header(admin_token), json=grant)
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


@pytest.mark.skip(reason="This is not implemented yet.")
def test_remove_grant(admin_token):
    url = f"{APP_URL}/admin/remove_grant"
    grant = grant(username='knut')
    response = requests.post(url, headers=auth_header(admin_token), json=grant)
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


@pytest.mark.skip(reason="This is not implemented yet.")
def test_add_grants(admin_token):
    url = f"{APP_URL}/admin/add_grants"
    response = requests.post(url, headers=auth_header(admin_token), json=dict(grants=[grant(username='knut') for _ in range(10)]))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'



# DOORS

def test_open_valid_door(admin_token):
    """ Our admin also has the grant to open the door currently in DEV environment """
    url = f"{APP_URL}/open?door_id={VALID_DOOR_ID}"
    response = requests.post(url, headers=auth_header(admin_token))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'

def test_open_invalid_door(admin_token):
    url = f"{APP_URL}/open?door_id={INVALID_DOOR_ID}"
    response = requests.post(url, headers=auth_header(admin_token))
    assert response.status_code == 422


# INFO

@pytest.mark.skip(reason="This is not implemented yet.")
def test_get_info_about_backend():
    url = f"{APP_URL}/info"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json().get('status') == 'success'

