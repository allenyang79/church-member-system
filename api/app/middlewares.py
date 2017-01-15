# -*- coding: utf-8 -*-
import datetime
from flask import current_app
from flask import session
from flask import request

from app import error
from app import auth
from app.config import config


def apply_middlewares(app, *middlewares):
    for mid in middlewares:
        if hasattr(mid, '__call__'):
            app = mid(app)
    return app

def wrap_cors(app):
    """Wrap cors support.
    """

    @app.before_request
    def option_autoreply():
        if request.method == 'OPTIONS':
            resp = current_app.make_default_options_response()
            if hasattr(resp, 'headers'):
                h = resp.headers
                # Allow the origin which made the XHR
                h['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
                # Allow Credentials
                h['Access-Control-Allow-Credentials'] = 'true'
                # Allow the actual method
                h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
                # Allow for cache $n seconds
                h['Access-Control-Max-Age'] = 3600 if config.get('global', "mode") == "production" else 1
                # We also keep current headers
                if 'Access-Control-Request-Headers' in request.headers:
                    h['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '')
            return resp

    @app.after_request
    def allow_origin(resp):
        if request.method == 'OPTIONS':
            return resp
        if hasattr(resp, 'headers'):
            h = resp.headers
            h['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', '')
            h['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
            h['Access-Control-Max-Age'] = 1728000
        return resp

    return app


def wrap_error_handler(app):
    @app.errorhandler(error.InvalidError)
    def handle_invalid_error(error):
        if isinstance(error, auth.UnauthorizedError):
            return {'success': False, 'message': 'Unauthorized.'}, error.status_code
        elif isinstance(error, auth.LoginFailError):
            return {'success': False, 'message': 'Login fail.'}, error.status_code
        return error.to_dict(), error.status_code
    return app



def wrap_session(app):
    @app.before_request
    def before_request():
        session.permanent = True
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)
    return app
