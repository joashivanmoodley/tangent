# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from employee.forms import LoginForm
from employee.functions import get_auth_token, set_search_url
from employee.functions import get_stats, login_check
from django.views.generic import View
from django.conf import settings
from datetime import datetime, timedelta

import requests


class Login(View):
    '''
    Home Page Prompting the user for login details
    '''
    template_vars = {}

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        self.template_vars['form'] = form
        return render(request, 'login.html', self.template_vars)

    def post(self, request, *args, **kwargs):

        form = LoginForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            auth_token = get_auth_token(form_data['username'], form_data['password'])
            if auth_token:
                request.session['authenticated'] = True
                request.session['auth_token'] = auth_token
                if 'invalid_login' in request.session:
                    del request.session['invalid_login']
                return redirect('employee_dashboard')
            else:
                if 'authenticated' in request.session:
                    del request.session['authenticated']
                if 'auth_token' in request.session:
                    del request.session['auth_token']
                request.session['invalid_login'] = True
            return redirect('login')


class SummaryView(View):
    '''
    This view is designed to display all employee data
    '''
    template_vars = {}
    url = ''

    def get(self, request, *args, **kwargs):
        HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
        r = requests.get(
            '%s/api/employee/' % (settings.API_BASE_POINT),
            headers=HEADERS
        )
        if r.status_code == 200:
            self.template_vars['data'] = r.json()
        return render(request, 'summary.html', self.template_vars)

    def post(self, request, *args, **kwargs):
        # this handles the search for employees
        self.url = set_search_url(request)
        HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}

        if request.POST:
            url = set_search_url(request)

        r = requests.get(
            '%s/api/employee/%s' % (settings.API_BASE_POINT, url),
            headers=HEADERS
        )
        if r.status_code == 200:
            self.template_vars['data'] = r.json()
        return render(request, 'summary.html', self.template_vars)

summary = login_check(SummaryView.as_view())


class DetailsView(View):
    '''
    Details view of employee it. If theres an id in kwargs then its for another user.
    If there is not an id in kwargs then the logined users details will be displayed.
    '''

    full_profile = False
    data = None
    template_vars = {}

    def get(self, request, *args, **kwargs):
        HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
        if 'id' not in kwargs:
            url = '%s/api/employee/me/' % (settings.API_BASE_POINT)
            r = requests.get(
                url,
                headers=HEADERS
            )
            self.full_profile = True
            if r.status_code == 200:
                self.data = r.json()
        else:

            url = '%s/api/employee/?user=%s' % (settings.API_BASE_POINT, kwargs['id'])
            r = requests.get(
                url,
                headers=HEADERS
            )
            if r.status_code == 200:
                self.data = r.json()[0]
            else:
                return redirect('summary')
        if 'id_number' not in self.data or not self.full_profile:
            self.template = 'details.html'
        else:
            self.template = 'super_user_details.html'

        self.template_vars['data'] = self.data
        return render(request, self.template, self.template_vars)

details = login_check(DetailsView.as_view())


def logout(request):
    if 'authenticated' in request.session:
        del request.session['authenticated']
    if 'auth_token' in request.session:
        del request.session['auth_token']

    return redirect('login')


class EmployeeDashView(View):
    '''
    This is the first view the user is directed to after login, and displays some basic stats
    '''

    template_vars = {}
    data = None
    position_data = []
    birthdays_this_month = 0

    def get(self, request, *args, **kwargs):
        HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
        r = requests.get(
            '%s/api/employee/' % (settings.API_BASE_POINT),
            headers=HEADERS
        )

        if r.status_code == 200:
            self.data = r.json()
        total_employees = len(self.data)

        for d in self.data:
            self.position_data.append(d['position'])
            user_birthday_month = datetime.strptime(d['birth_date'], '%Y-%m-%d').month
            if user_birthday_month == datetime.now().month:
                self.birthdays_this_month = self.birthdays_this_month + 1

        url = '%s/api/employee/me/' % (settings.API_BASE_POINT)
        r = requests.get(
            url,
            headers=HEADERS
        )
        if r.status_code == 200:
            emp_data = r.json()
            self.template_vars['leave_remaining'] = emp_data['leave_remaining']

            if datetime.strptime(emp_data['next_review'], '%Y-%m-%d')  > datetime.now(): 
                self.template_vars['next_review'] = emp_data['next_review']
            else:
                self.template_vars['next_review'] = 'No Reviews Scheduled'
            anni_start_date_this_year = datetime.strptime(emp_data['start_date'], '%Y-%m-%d').replace(year=datetime.now().year)
            days_till_anni = anni_start_date_this_year - datetime.now()+ timedelta(days=1)
            if days_till_anni.days < 0:
                days_till_anni = days_till_anni +  timedelta(days=365)
            self.template_vars['days_till_anni'] = days_till_anni.days
        self.template_vars['total_employees'] = total_employees
        self.template_vars['birthdays_this_month'] = self.birthdays_this_month
        self.template_vars['position_data'] = self.position_data
        self.template_vars['month'] = datetime.now().month
        return render(request, 'employee_dashboard.html', self.template_vars)

employee_dashboard = login_check(EmployeeDashView.as_view())


class BirthdayView(View):
    '''
    Displays info of birthdays in the month.
    '''

    template_vars = {}
    data = None

    def get(self, request, *args, **kwargs):
        HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
        r = requests.get(
            '%s/api/employee/?birth_date_range=3' % (settings.API_BASE_POINT),
            headers=HEADERS
        )

        if r.status_code == 200:
            self.data = r.json()

        self.template_vars['data'] = self.data
        return render(request, 'birthday.html', self.template_vars)

birthday = login_check(BirthdayView.as_view())


class ReviewView(View):
    '''
    Displays info of logined users reviews.
    '''
    template_vars = {}
    data = None

    def get(self, request, *args, **kwargs):
        HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
        r = requests.get(
            '%s/api/review/' % (settings.API_BASE_POINT),
            headers=HEADERS
        )

        if r.status_code == 200:
            self.data = r.json()

        self.template_vars['data'] = self.data
        return render(request, 'review.html', self.template_vars)

review = login_check(ReviewView.as_view())


class EmployeeStatsView(View):
    '''
    Displays company position info.
    '''
    template_vars = {}
    data = None

    def get(self, request, *args, **kwargs):
        
        HEADERS = {'Authorization': 'Token %s' % request.session['auth_token']}
        r = requests.get(
            '%s/api/employee/' % (settings.API_BASE_POINT),
            headers=HEADERS
        )
        if r.status_code == 200:
            self.data = r.json()

        total_employees = len(self.data)
        self.template_vars['data'] = self.data
        

        gender_data, position_data, race_data, employee_data = get_stats(self.data)
        self.template_vars['gender_data'] = gender_data
        self.template_vars['total_employees'] = total_employees
        self.template_vars['position_data'] = position_data
        self.template_vars['race_data'] = race_data
        self.template_vars['month'] = datetime.now().month
        self.template_vars['employee_data'] = employee_data
        return render(request, 'employee_stats.html', self.template_vars)

employee_stats = login_check(EmployeeStatsView.as_view())
