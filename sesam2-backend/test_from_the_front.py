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
from random import randint


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
    url = f"{APP_URL}/admin/user"
    for name in ['susan', 'berit', 'harriberat', 'jhoroo']:
        response = requests.post(url, headers=auth_header(admin_token), json=dict(username=name))
        assert response.status_code == 200
        assert response.json().get('status') == 'success'

    response = requests.post(url, headers=auth_header(admin_token), json=dict(username='knut'))
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
    url = f"{APP_URL}/admin/user"
    response = requests.post(url, headers=auth_header(normal_token), json=dict(username='sue'))
    assert response.status_code == 401
    assert response.json().get('detail') == 'Not enough permissions'


def test_update_user(admin_token):
    url = f"{APP_URL}/admin/user"
    response = requests.patch(url, headers=auth_header(admin_token), json=dict(username='knut', is_admin=True))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'
    response = get_token('knut', 'knut')
    token = response.json()
    decoded = decode_token(token)
    assert decoded.get('is_admin') == True
    requests.post(url, headers=auth_header(admin_token), json=dict(username='knut', is_admin=True))


def test_delete_user(admin_token):
    url = f"{APP_URL}/admin/user"
    response = requests.post(url, headers=auth_header(admin_token), json=dict(username='tobedeleted'))
    response = requests.delete(url, headers=auth_header(admin_token), json=dict(username='tobedeleted'))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


def test_delete_user_by_normal_user_fails(normal_token):
    url = f"{APP_URL}/admin/user"
    response = requests.delete(url, headers=auth_header(normal_token), json=dict(username='test'))
    assert response.status_code == 401


def grant(*, door_uuid = VALID_DOOR_ID, weekday = randint(1,7), grant_start = randint(0,23), grant_end = randint(0,23)):
    return dict(door_uuid=door_uuid, weekday=weekday, grant_start=grant_start, grant_end=grant_end)


def test_add_and_delete_grants_to_users(admin_token):
    url = f"{APP_URL}/admin/grants"
    grants = [grant() for _ in range(10)]
    # valid one now
    grants.append(grant(weekday=now.isoweekday(), grant_start=now.hour, grant_end=now.hour + 1))
    response = requests.put(url, headers=auth_header(admin_token), json=dict(target='user', target_name='knut', grants=grants))
    if response.status_code != 200:
        print(response.json())
    assert response.status_code == 200
    assert response.json().get('status') == 'success'

    response = requests.put(url, headers=auth_header(admin_token), json=dict(target='user', target_name='knut', grants=[]))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


def test_create_group(admin_token):
    url = f"{APP_URL}/admin/group"
    response = requests.post(url, headers=auth_header(admin_token), json=dict(name='testgroup', description='this is a test group'))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'



def test_add_and_delete_grants_to_groups(admin_token):
    url = f"{APP_URL}/admin/grants"
    grants = [grant() for _ in range(10)]
    # valid one now
    grants.append(grant(weekday=now.isoweekday(), grant_start=now.hour, grant_end=now.hour + 1))
    response = requests.put(url, headers=auth_header(admin_token), json=dict(target='group', target_name='testgroup', grants=grants))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'

    response = requests.put(url, headers=auth_header(admin_token), json=dict(target='group', target_name='testgroup', grants=[]))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


def test_add_user_to_group(admin_token):
    url = f"{APP_URL}/admin/usergroup"
    response = requests.put(url, headers=auth_header(admin_token), json=dict(username='knut', groupname='testgroup'))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


def test_remove_user_from_group(admin_token):
    url = f"{APP_URL}/admin/group"
    requests.post(url, headers=auth_header(admin_token), json=dict(name='testgroup2', description='this is a test group'))
    # put user in group
    url = f"{APP_URL}/admin/usergroup"
    requests.put(url, headers=auth_header(admin_token), json=dict(username='knut', groupname='testgroup2'))
    # remove user from group
    response = requests.delete(url, headers=auth_header(admin_token), json=dict(username='knut', groupname='testgroup2'))
    if response.status_code != 200:
        print(response.text)
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


def test_update_group(admin_token):
    url = f"{APP_URL}/admin/group"
    response = requests.patch(url, headers=auth_header(admin_token), json=dict(name='testgroup', description='this is the best group ever'))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'


def test_delete_group(admin_token):
    url = f"{APP_URL}/admin/group"
    response = requests.delete(url, headers=auth_header(admin_token), json=dict(name='testgroup'))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'

# def test_add_user_to_group(admin_token):
#     url = f"{APP_URL}/admin/group"
#     response = requests.post(url, headers=auth_header(admin_token), json=dict(group='testgroup', user='knut'))

# DOORS

def test_open_valid_door(admin_token):
    """ Our admin also has the grant to open the door currently in DEV environment """
    url = f"{APP_URL}/open?door_id={VALID_DOOR_ID}"
    response = requests.post(url, headers=auth_header(admin_token))
    assert response.status_code == 200
    assert response.json().get('status') == 'success'
    # we do some more to manually check the db for the increment
    requests.post(url, headers=auth_header(admin_token))
    requests.post(url, headers=auth_header(admin_token))
    requests.post(url, headers=auth_header(admin_token))

def test_open_invalid_door(admin_token):
    url = f"{APP_URL}/open?door_id={INVALID_DOOR_ID}"
    response = requests.post(url, headers=auth_header(admin_token))
    assert response.status_code == 422


# INFO

def test_get_info_about_backend():
    url = f"{APP_URL}/are-we-online"
    response = requests.get(url)
    assert response.status_code == 200
