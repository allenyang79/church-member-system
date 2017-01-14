# -*- coding: utf-8 -*-

from flask import Flask, Response
from flask import make_response
from werkzeug.routing import BaseConverter

import json
import bson
import bson.json_util


class CustomResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        status = headers = None
        if isinstance(rv, tuple):
            rv, status, headers = rv + (None,) * (3 - len(rv))

        if isinstance(rv, (dict, list)):
            rv = json.dumps(rv)  # , **JSON_OPTIONS
            if headers is None:
                headers = {}
            headers['content-type'] = 'application/json'
        rv = Response(rv, status, headers)
        return super(CustomResponse, cls).force_type(rv, environ)


class CustomFlask(Flask):
    response_class = CustomResponse


class BSONJSONEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return bson.json_util.default(o)
        except Exception as e:
            return super(BSONJSONEncoder, self).default(o)


class BSONJSONDecoder(json.JSONDecoder):
    """ Do nothing custom json decoder """

    def __init__(self, *args, **kargs):
        _ = kargs.pop('object_hook', None)
        super(BSONJSONDecoder, self).__init__(object_hook=bson.json_util.object_hook, *args, **kargs)


class ObjectIdConverter(BaseConverter):
    def to_python(self, value):
        return bson.ObjectId(value)

    def to_url(self, value):
        return BaseConverter.to_url(value['$oid'])

