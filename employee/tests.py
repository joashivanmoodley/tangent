# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import resolve
from django.test import TestCase
from employee.views import Login
from selenium import webdriver
from django.test import RequestFactory
from django.test.client import Client


class Test(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.factory = RequestFactory()
        self.client = Client()

    def tearDown(self):
        self.browser.quit()

    def test_auth_success(self):
        '''
        User comes to the home page tries to Login
        User enters the correct login details and is then redirected to the summary page.
        '''
        request = self.factory.get(resolve('/'))
        response = Login.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'username': 'pravin.gordhan',
            'password': 'pravin.gordhan'
        }
        request = self.factory.post(resolve('/'), data)
        request.session = self.client.session
        response = Login.as_view()(request)
        self.assertEqual(response.url, '/employee/summary/')

    def test_auth_fail(self):
        '''
        User comes to the home page tries to Login
        User enters the incorrect login details and is then redirected to the login page.
        '''
        request = self.factory.get(resolve('/'))
        response = Login.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'username': 'pravin.gordhan',
            'password': 'wrong password'
        }
        request = self.factory.post(resolve('/'), data)
        request.session = self.client.session
        response = Login.as_view()(request)
        self.assertEqual(response.url, '/')
