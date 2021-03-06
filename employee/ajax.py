from django.http import HttpResponse
from django.conf import settings
import requests
import json
from django.template import RequestContext, loader



def search_filter(request):
    """
    Populates the search bar dropdowns
    """

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
        user_data.append({
            'id': d['user']['id'],
            'name': '%s %s' % (d['user']['first_name'], d['user']['last_name'])
        })

    search_data.append({
        'position': position_data,
        'user_data': user_data
    })
    return HttpResponse(json.dumps(search_data))


def request_download(request):
    """
    Sends data to micoservice to process.
    """
    if request.POST:
        section = request.POST.get('section', None)
        download_type = request.POST.get('download_type', None)
        email = request.POST.get('email', None)

        if section and download_type and email:
            HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
            r = requests.get(
                '%s/api/employee/' % (settings.API_BASE_POINT),
                headers=HEADERS
            )
            if r.status_code == 200:
                data = r.json()
                template = loader.get_template('emails/email_summary.html')
                html = template.render({'data': data})
                r = requests.post(
                    '%s/process-data/' % settings.PDF_XLS_SERVICE_URL,
                    data={
                        'download_type': download_type,
                        'email': email,
                        'html': html,
                        'data': json.dumps(data)
                    }
                )
                if r.status_code == 200:
                    return HttpResponse(r.json()['status'])

    return HttpResponse("fail")