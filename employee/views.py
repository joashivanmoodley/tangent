# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse
from employee.forms import LoginForm
from employee.functions import get_auth_token
from django.views.generic import View
from django.conf import settings

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
                return redirect('employee_summary')
            else:
                if 'authenticated' in request.session:
                    del request.session['authenticated']
                if 'auth_token' in request.session:
                    del request.session['auth_token']
            return redirect('login')


def summary(request):
    '''
    Summary view displaying all employee info
    '''
    template = 'summary.html'
    template_vars = {}
    if 'authenticated' not in request.session or 'auth_token' not in request.session:
        return redirect('login')

    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token'],}
    url = '?'
    if request.POST:
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

    r = requests.get(
        '%s/api/employee/%s' % (settings.API_BASE_POINT, url),
        headers=HEADERS
    )
    if r.status_code == 200:
        print r.json()
        template_vars['data'] = r.json()

    return render(request, template, template_vars)


def details(request, id=None):
    '''
    details view for a specific user.
    '''
    full_profile = False
    data = None
    # Checks if User is authenticated by checkinf for a session var set on successful login
    if 'authenticated' not in request.session or 'auth_token' not in request.session:
        return redirect('login')

    template_vars = {}
    HEADERS = {'Authorization': 'Token %s' % request.session['auth_token'],}
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
