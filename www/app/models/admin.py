# -*- coding: utf-8 -*-

import functools
from schematics.models import Model
from schematics.types import StringType, BooleanType, ListType
from passlib.hash import pbkdf2_sha256

import flask_login

from app import error
from app.db import db
from app.permissions import ROLES, PERMISSIONS
from app.models.utils import get_increment_id


class AdminModel(Model, flask_login.UserMixin):

    username = StringType(required=True)
    name = StringType(default=lambda: '')
    description = StringType(default=lambda: '')
    roles = ListType(StringType, default=lambda: [])
    enabled = BooleanType(default=lambda: True)

    @classmethod
    def get_one(cls, username):
        raw = db.admins.find_one({'username': username}, {'_id': False, 'password': False})
        if raw:
            return AdminModel(raw)
        return None

    @classmethod
    def fetch(cls, query={}):
        return [cls(raw) for raw in db.admins.find(query, {'_id': False, 'password': False})]

    @classmethod
    def hash_password(cls, password):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        return pbkdf2_sha256.encrypt(password, rounds=10 ** 5, salt_size=16)

    @classmethod
    def create(cls, username, password, roles=None):
        if not username:
            raise error.InvalidError('`username` is required')
        if not password:
            raise error.InvalidError('`password` is required')
        if cls.get_one(username):
            raise error.InvalidError('`%s` was existed' % username)

        raw = {}
        raw['_id'] = get_increment_id(_id='admins')
        raw['username'] = username
        raw['password'] = cls.hash_password(password)

        if isinstance(roles, list):
            raw['roles'] = roles

        result = db.admins.insert_one(raw)
        return cls.get_one(username)

    def save(self):
        self.validate()
        to_save = {k: v for k, v in self.to_primitive().items() if k in (
            'name',
            'enabled',
            'roles',
            'description'
        )}
        result = db.admins.update_one({
            'username': self.username,
        }, {
            '$set': to_save
        })
        return result.matched_count > 0

    def update_password(self, password):
        result = db.admins.update_one({
            'username': self.username,
        }, {
            '$set': {
                'password': self.__class__.hash_password(password)
            }
        }, upsert=True)
        return result.matched_count

    def validate_password(self, password):
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        raw = db.admins.find_one({'username': self.username}, {'password': True})
        if raw and raw.get('password'):
            return pbkdf2_sha256.verify(password, raw.get('password'))
        return False

    def can_modify(self, someone):
        """
        :params AdminModel who:
        """
        if self.username == someone.username:
            return True
        if self.has_permissions(PERMISSIONS.ROOT):
            return True
        if someone.has_permissions(PERMISSIONS.ROOT):
            return False
        if self.has_permissions(PERMISSIONS.WRITE_ADMIN):
            return True
        return False

    @property
    def permissions(self):
        if hasattr(self, '_permissions'):
            return self._permissions
        setattr(self, '_permissions', set())
        for role in self.roles:
            self._permissions = self._permissions | ROLES[role]
        return self._permissions

    def has_permissions(self, permissions):
        if PERMISSIONS.ROOT in self.permissions:
            return True
        if isinstance(permissions, basestring):
            permissions = [permissions]
        permissions = set(permissions)
        return not (permissions - self.permissions)

    def as_dict(self):
        ret = self.to_primitive()
        ret['permissions'] = list(self.permissions)
        return ret

    # implement UserMixin
    def get_id(self):
        return self.username

    @property
    def is_authenticated(self):
        return self.enabled

