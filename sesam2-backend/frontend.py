import requests
import jose
from jose import jwt


## TEST file to develop with
username = 'dev'
password = 'dev'
door_id = "001b823d-1f5c-4f39-9e74-015bb2dcef8f"
app_url="http://localhost:8000"
#


def get_token() -> str:

    # get the token from url
    url = f"{app_url}/token?username={username}&password={password}"
    response = requests.post(url)
    return response.json()

def decode_token(token):
    return jwt.get_unverified_claims(token['access_token'])

token = get_token()
token_info = decode_token(token)
broken_token = token.copy()
broken_token['access_token'] = broken_token['access_token'] + "1"
assert token.get('access_token')


def auth_header(token):
    return {
        'Authorization': f'Bearer {token.get("access_token")}',
        'Content-Type': 'application/json',
    }

def open_door(token: str, door_id: str = door_id) -> str:
    url = f"{app_url}/open?door_id={door_id}"
    response = requests.post(url, headers=auth_header(token))
    return response.json()

response = open_door(broken_token)
assert not response.get('status') == 'success'
response = open_door(token)
assert response.get('status') == 'success'

