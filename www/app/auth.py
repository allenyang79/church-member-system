# -*- coding: utf-8 -*-

import functools
import json
import os
import sys
import time
import datetime
import traceback
import binascii

from flask import Flask
from flask import current_app, g
from flask import request, make_response, redirect, url_for
from flask import Blueprint
import flask_login

#import jwt

from app import error
from app.config import config
from app.models import AdminModel


class LoginFailError(error.InvalidError):
    def __init__(self, message='Login fail.', status_code=401):
        super(LoginFailError, self).__init__(message, status_code)


class UnauthorizedError(error.InvalidError):
    def __init__(self, message='Unauthorized.', status_code=401):
        super(UnauthorizedError, self).__init__(message, status_code)


class AnonymousUser(flask_login.AnonymousUserMixin):
    def __init__(self):
        self.username = None
        self._is_authenticated = False

    def get_id(self):
        return None

    @property
    def is_authenticated(self):
        return False

    def as_dict(self):
        return {
            'username': self.username,
            'is_authenticated': False
        }


def init(app):
    """Init login_manger on app."""
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = AnonymousUser

    @login_manager.user_loader
    def user_loader(username):
        user = AdminModel.get_one(username)
        return user

    @app.before_request
    def validate_auth_before_request():
        if hasattr(request, 'url_rule') and hasattr(request.url_rule, 'endpoint'):
            endpoint = request.url_rule.endpoint
        else:
            endpoint = None

        white_list = (
            'index',
            'heartbeat',
            'auth.login',
        )
        if endpoint and endpoint not in white_list :
            if not flask_login.current_user.is_authenticated:
                raise UnauthorizedError()
                #return current_app.login_manager.unauthorized()
    return login_manager


def wrap_auth(app):
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    app.extensions['login_manager'] = init(app)
    return app


def me():
    return flask_login.current_user


blueprint = Blueprint('auth', __name__)

@blueprint.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    user = AdminModel.get_one(payload.get('username', '').lower())
    if not user:
        raise LoginFailError()

    if not user.validate_password(payload.get('password')):
        raise LoginFailError()

    flask_login.login_user(user)
    return {
        'success': True,
        'data': me().as_dict()
    }


@blueprint.route('/logout')
def logout():
    flask_login.logout_user()
    return {
        'success': True,
        'message': 'logout success.'
    }


@blueprint.route('/user/me')
def user_me():
    return {
        'success': True,
        'data': me().as_dict()
    }

