from django.conf import settings
import requests


def get_auth_token(username, password):
    r = requests.post(
        '%s/api-token-auth/' % settings.API_BASE_POINT,
        data={
            'username': username,
            'password': password
        }
    )
    if r.status_code == 200:
        return r.json()['token']
    return False