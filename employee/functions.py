from django.conf import settings
from django.shortcuts import redirect

import requests


def get_auth_token(username, password):
    '''
    Gets authentication token needed to poll the api
    '''
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


def set_search_url(request):
    '''
    builds the url string to used to search for users
    '''

    url = '?'
    gender = request.POST.get('gender', None)
    race = request.POST.get('race', None)
    user = request.POST.get('user', None)
    position = request.POST.get('position', None)
    email = request.POST.get('email', None)

    if gender:
        if url == '?':
            url = url + 'gender=%s' % gender
        else:
            url = url + '&gender=%s' % gender
    if race:
        if url == '?':
            url = url + 'race=%s' % race
        else:
            url = url + '&race=%s' % race
    if user:
        if url == '?':
            url = url + 'user=%s' % user
        else:
            url = url + '&user=%s' % user
    if position:
        if url == '?':
            url = url + 'position=%s' % position
        else:
            url = url + '&position=%s' % position
    if email:
        if url == '?':
            url = url + 'email__contains=%s' % email
        else:
            url = url + '&email__contains=%s' % email
    return url


def login_check(function):
    '''
    custom decorator to handle custom authentication
    '''
    def wrap(request, *args, **kwargs):
        if 'authenticated' not in request.session or 'auth_token' not in request.session:
            return redirect('login')
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
