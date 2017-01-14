# -*- coding: utf-8 -*-

class Permissions(object):

    def __init__(self):
        self._permissions = set()

    def register(self, key):
        if isinstance(key, list):
            for _key in key:
                self.register(_key)
            return
        key = key.upper()
        self._permissions.add(key)

    def all_permissions(self):
        return set(self._permissions)

    def __getattr__(self, key):
        if key in self._permissions:
            return key
        raise Exception('unknow permission: %s' % key)

PERMISSIONS = Permissions()

PERMISSIONS.register([
    'ROOT',

    'READ_ADMIN',
    'WRITE_ADMIN',

    'READ_PERSON_LIST',
    'READ_PERSON',
    'WRITE_PERSON',

    'READ_GROUP_LIST',
    'READ_GROUP',
    'WRITE_GROUP',
])


ROLES = {
    'ROOT': PERMISSIONS.all_permissions(),
    'ADMIN': {
        PERMISSIONS.READ_PERSON_LIST,
        PERMISSIONS.READ_PERSON,
        PERMISSIONS.WRITE_PERSON,
        PERMISSIONS.READ_GROUP_LIST,
        PERMISSIONS.READ_GROUP,
        PERMISSIONS.WRITE_GROUP,
    },
    'VIEWER': {
        PERMISSIONS.READ_GROUP_LIST,
        PERMISSIONS.READ_PERSON_LIST,
    }
}
