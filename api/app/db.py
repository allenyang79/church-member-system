# -*- coding: utf-8 -*-

import os
import sys
import functools
import pymongo

from werkzeug.local import LocalProxy
from app.config import config

_db = None
_client = None


def _connect_db():
    client = pymongo.MongoClient(config.get('db', 'DB_HOST'), config.getint('db', 'DB_PORT'))
    db = client[config.get('db', 'DB_NAME')]
    return client, db


def find_db():
    global _client, _db
    if not _db:
        _client, _db = _connect_db()
    return _db

def init_db():
    print 'init admins by %s' % db.admins.create_index([('username', pymongo.ASCENDING)], unique=True)
    print 'init persons by %s' % db.persons.create_index([('person_id', pymongo.ASCENDING)], unique=True)
    print 'init groups by %s' % db.groups.create_index([('group_id', pymongo.ASCENDING)], unique=True)

db = LocalProxy(find_db)
