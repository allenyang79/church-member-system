# -*- coding: utf-8 -*-

import json
import sys
import time

from flask import Flask
from flask import current_app, g
from flask import url_for
from flask import request, redirect, jsonify
from werkzeug.routing import BaseConverter
from bson.objectid import ObjectId

from app import utils
from app import middlewares
from app.config import config
from app.logger import logger

from app import views
from app import auth

app = utils.CustomFlask(__name__)
app.config.update({k.upper(): v for k, v in config.items('flask')})
app = middlewares.apply_middlewares(app,
    middlewares.wrap_cors,
    middlewares.wrap_error_handler,
    middlewares.wrap_session,
    auth.wrap_auth
)


@app.route('/')
@app.route('/index')
def index():
    if config.get('global', 'mode') == 'production':
        return redirect('/static')
    return {
        'success': True,
        'ts': int(time.time())
    }

@app.route('/heartbeat')
def heartbeat():
    from app.db import db
    import pymongo
    now_ts = int(time.time())
    r = db.tests.find_one_and_update({'_id': 'test'}, {
        '$set': {'val': now_ts}
    }, upsert=True, return_document=pymongo.ReturnDocument.AFTER)
    return r

@app.route('/site')
def site():
    return {
        k: v for k,v in config.items('site')
    }

@app.route('/sitemap')
def sitemap():
    import cgi
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(map(lambda x:str(x), rule.methods))
        line = "{rule} [{methods}]".format(methods=methods, rule=cgi.escape(rule.rule))
        output.append(line)
    return '<br/>'.join(output)

app.register_blueprint(auth.blueprint)
app.register_blueprint(views.admin_view)
app.register_blueprint(views.person_view)
app.register_blueprint(views.group_view)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
