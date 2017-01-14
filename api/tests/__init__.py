# -*- coding: utf-8 -*-
import os, sys
import atexit
import re

import unittest
import mock

env = os.getenv('ENV')

if env != 'test':
    raise Exception('testing should run on ENV=TEST')

box = None

def setup():
    from mongobox import MongoBox
    global box, db, client
    box = MongoBox()
    box.start()

    def side_effect():
        client = box.client()  # pymongo client
        db = client['test']
        return client, db

    mock_init_db = mock.patch('app.db._init_db', side_effect=side_effect)
    mock_init_db.start()


def bye():
    global box
    if box:
        box.stop()

atexit.register(bye)
