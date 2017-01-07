# -*- coding: utf-8 -*-
import os
import sys

from app.config import config
from app.logger import logger
from app.db import db

import unittest
import mock


class TestDB(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_db(self):
        """Test mock db is working."""

        db.tests.insert_one({'_id': '1234'})
        one = db.tests.find_one()
        self.assertTrue(one)
        db.tests.drop()

    def test_load_config(self):
        """test config read right."""
        self.assertEqual(config.get('global', 'MODE'), 'test')
