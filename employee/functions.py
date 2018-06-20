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
    url_str = '?'
    for k, v in request.POST.items():
        if k != 'csrfmiddlewaretoken': 
           search ='%s=%s&' % (k, v)
           url_str= url_str + search
    return url_str


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


def get_stats(data):
    position_data = {}
    gender_data = {'male': 0, 'female': 0}
    race_data = {'B': 0, 'C': 0, 'I': 0, 'W': 0, 'N': 0}
    employee_data = {
        'most_recent':  {'name': '', 'value': 0, 'id': None},
        'longest':  {'name': '', 'value': 0, 'id': None},
        'youngest':  {'name': '', 'value': 0, 'id': None},
        'oldest':  {'name': '', 'value': 0, 'id': None},
    }
    for d in data:

        if d['gender'] == 'M':
            gender_data['male'] += 1
        else:
            gender_data['female'] += 1

        race_data[d['race']] += 1

        if d['years_worked'] > employee_data['longest']['value'] or employee_data['longest']['value'] == 0:
            employee_data['longest']['name'] = '%s %s' % (d['user']['first_name'], d['user']['last_name'])
            employee_data['longest']['value'] = d['years_worked']
            employee_data['longest']['id'] = d['user']['id']

        if d['years_worked'] < employee_data['most_recent']['value'] or employee_data['most_recent']['value'] == 0:
            employee_data['most_recent']['name'] = '%s %s' % (d['user']['first_name'], d['user']['last_name'])
            employee_data['most_recent']['value'] = d['years_worked']
            employee_data['most_recent']['id'] = d['user']['id']

        if d['age'] < employee_data['youngest']['value'] or employee_data['youngest']['value'] == 0:
            employee_data['youngest']['name'] = '%s %s' % (d['user']['first_name'], d['user']['last_name'])
            employee_data['youngest']['value'] = d['age']
            employee_data['youngest']['id'] = d['user']['id']

        if d['age'] > employee_data['oldest']['value'] or employee_data['oldest']['value'] == 0:
            employee_data['oldest']['name'] = '%s %s' % (d['user']['first_name'], d['user']['last_name'])
            employee_data['oldest']['value'] = d['age']
            employee_data['oldest']['id'] = d['user']['id']

        # gets a list of positions and their respective counts
        if d['position']['name'] not in position_data.keys():
            if d['position']['level'] == 'Junior':
                position_data.update({
                    d['position']['name']: {d['position']['level']: 1, 'Senior': 0}
                })
            else:
                position_data.update({
                    d['position']['name']: {d['position']['level']: 1, 'Junior': 0}
                })
        else:
            if d['position']['level'] not in position_data[d['position']['name']].keys():
                position_data[d['position']['name']][d['position']['level']] = 1
            else:
                position_data[d['position']['name']][d['position']['level']] += 1
    return gender_data, position_data, race_data, employee_data