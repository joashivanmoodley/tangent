from django.http import HttpResponse
from django.conf import settings
import requests
import json


def search_filter(request):
    data = None
    position_data = []
    positions_added = []
    user_data = []
    search_data = []
    if 'authenticated' not in request.session or 'auth_token' not in request.session:
        return False
    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}

    r = requests.get(
        '%s/api/employee/' % (settings.API_BASE_POINT),
        headers=HEADERS
    )
    if r.status_code == 200:
        data = r.json()

    for d in data:
        if d['position']['id'] not in positions_added:
            position_data.append({
                'id': d['position']['id'],
                'name': d['position']['name']
            })
            positions_added.append(d['position']['id'])
        user_data.append({'id': d['user']['id'], 'name': '%s %s' % (d['user']['first_name'], d['user']['last_name'])})

    search_data.append({
        'position': position_data,
        'user_data': user_data
    })
    return HttpResponse(json.dumps(search_data))