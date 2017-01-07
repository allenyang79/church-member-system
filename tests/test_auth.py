# -*- coding: utf-8 -*-

import Cookie
import os
import sys
import json
import unittest
import bson

import werkzeug.http
import jwt

from app.main import init_app
from app.config import config
from app.db import db
from app.error import InvalidError
from app.auth import UnauthorizedError, LoginFailError
from app.models import AdminModel

import mock


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.main_app = init_app()
        cls.main_app.debug = True

    def setUp(self):
        self.client = self.main_app.test_client()

    def tearDown(self):
        pass

    def test_login(self):
        """test_login"""
        payload = {
            'username': config.get('auth', 'DEFAULT_ADMIN_USERNAME'),
            'password': config.get('auth', 'DEFAULT_ADMIN_PASSWORD')
        }
        r = self.client.post('/login', data=json.dumps(payload), content_type='application/json')
        r = json.loads(r.data)
        self.assertEqual(r['success'], True)

        r = self.client.get('/me')
        r = json.loads(r.data)
        self.assertEqual(r['data']['username'], config.get('auth', 'DEFAULT_ADMIN_USERNAME'))

        r = self.client.post('/logout', data=json.dumps(payload), content_type='application/json')
        r = json.loads(r.data)
        self.assertEqual(r['success'], True)

        r = self.client.get('/me')
        self.assertEqual(r.status_code, 403)

    def test_login_fail(self):
        payload = {
            'username': config.get('auth', 'DEFAULT_ADMIN_USERNAME'),
            'password': 'anything'
        }
        r = self.client.post('/login', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 401)

        payload = {}
        r = self.client.post('/login', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 401)

        r = self.client.get('/me')
        self.assertEqual(r.status_code, 403)
