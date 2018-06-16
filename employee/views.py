# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from employee.forms import LoginForm
from employee.functions import get_auth_token, set_search_url, login_check
from django.views.generic import View
from django.conf import settings
from datetime import datetime

import requests


class Login(View):
    '''
    Home Page Prompting the user for login details
    '''
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        template_vars = {'form': form}
        return render(request, 'login.html', template_vars)

    def post(self, request, *args, **kwargs):

        form = LoginForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            auth_token = get_auth_token(form_data['username'], form_data['password'])
            if auth_token:
                request.session['authenticated'] = True
                request.session['auth_token'] = auth_token
                return redirect('employee_dashboard')
            else:
                if 'authenticated' in request.session:
                    del request.session['authenticated']
                if 'auth_token' in request.session:
                    del request.session['auth_token']
            return redirect('login')


@login_check
def summary(request):
    '''
    Summary view displaying all employee info
    '''
    template = 'summary.html'
    template_vars = {}
    url = ''
    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}

    if request.POST:
        url = set_search_url(request)

    r = requests.get(
        '%s/api/employee/%s' % (settings.API_BASE_POINT, url),
        headers=HEADERS
    )
    if r.status_code == 200:
        template_vars['data'] = r.json()

    return render(request, template, template_vars)


@login_check
def details(request, id=None):
    '''
    details view for a specific user.
    '''
    full_profile = False
    data = None
    template_vars = {}
    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}

    if not id:
        url = '%s/api/employee/me/' % (settings.API_BASE_POINT)
        r = requests.get(
            url,
            headers=HEADERS
        )
        full_profile = True
        if r.status_code == 200:
            data = r.json()
    else:

        url = '%s/api/employee/?user=%s' % (settings.API_BASE_POINT, id)
        r = requests.get(
            url,
            headers=HEADERS
        )
        if r.status_code == 200:
            data = r.json()[0]
        else:
            return redirect('summary')

    template_vars['data'] = data

    if 'id_number' not in data or not full_profile:
        template = 'details.html'
    else:
        template = 'super_user_details.html'

    template_vars['full_profile'] = full_profile

    return render(request, template, template_vars)


def logout(request):
    if 'authenticated' in request.session:
        del request.session['authenticated']
    if 'auth_token' in request.session:
        del request.session['auth_token']

    return redirect('login')


@login_check
def employee_dashboard(request):

    template = 'employee_dashboard.html'
    template_vars = {}
    data = None
    position_data = []
    birthdays_this_month = 0

    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
    r = requests.get(
        '%s/api/employee/' % (settings.API_BASE_POINT),
        headers=HEADERS
    )

    if r.status_code == 200:
        data = r.json()
    total_employees = len(data)

    for d in data:
        position_data.append(d['position'])
        user_birthday_month = datetime.strptime(d['birth_date'], '%Y-%m-%d').month
        if user_birthday_month == datetime.now().month:
            birthdays_this_month = birthdays_this_month + 1

    template_vars['total_employees'] = total_employees
    template_vars['birthdays_this_month'] = birthdays_this_month
    template_vars['position_data'] = position_data
    template_vars['month'] = datetime.now().month

    return render(request, template, template_vars)


@login_check
def birthday(request):

    template = 'birthday.html'
    template_vars = {}
    data = None

    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
    r = requests.get(
        '%s/api/employee/?birth_date_range=3' % (settings.API_BASE_POINT),
        headers=HEADERS
    )

    if r.status_code == 200:
        data = r.json()

    template_vars['data'] = data

    return render(request, template, template_vars)


@login_check
def review(request):

    template = 'review.html'
    template_vars = {}
    data = None

    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
    r = requests.get(
        '%s/api/review/' % (settings.API_BASE_POINT),
        headers=HEADERS
    )

    if r.status_code == 200:
        data = r.json()

    template_vars['data'] = data

    return render(request, template, template_vars)


@login_check
def position(request):

    template = 'position.html'
    template_vars = {}
    data = None
    position_data = {}

    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
    r = requests.get(
        '%s/api/employee/' % (settings.API_BASE_POINT),
        headers=HEADERS
    )
    if r.status_code == 200:
        data = r.json()

    total_employees = len(data)

    for d in data:
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

    template_vars['total_employees'] = total_employees
    template_vars['position_data'] = position_data
    template_vars['month'] = datetime.now().month

    return render(request, template, template_vars)
