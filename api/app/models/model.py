# -*- coding: utf-8 -*-

import bson
import bson.objectid

from schematics.models import Model
from custom_types import MongoIdType

from app.db import db
from app import error


class CollectionProperty(object):
    def __init__(self, collection_name):
        self.collection_name = collection_name

    def __get__(self, instance, cls):
        if self.collection_name is None:
            raise NotImplementedError('please custom a collection name for save documents.')

        return db.get_collection(self.collection_name)

    def __set__(self, instance, value):
        raise Exception('CollectionProperty is a readonly property.')


class DocumentModel(Model):
    class Options:
        serialize_when_none = False

    collection = CollectionProperty(None)
    _id = MongoIdType(required=True, serialized_name='_id', default=lambda: bson.objectid.ObjectId())

    @classmethod
    def get(cls, _id):
        if not isinstance(_id, bson.objectid.ObjectId):
            _id = bson.objectid.ObjectId(_id)

        native = cls.collection.find_one({'_id': _id})
        if native:
            return cls(native, strict=False)
        return None

    @classmethod
    def get_one(cls, key, value):
        native = cls.collection.find_one({key: value})
        if native:
            return cls(native, strict=False)
        return None

    @classmethod
    def fetch(cls, query={}, fields=None):
        for native in cls.collection.find(query, fields):
            yield cls(native)

    @classmethod
    def create(cls, payload):
        instance = cls(payload)
        instance.validate()
        result = cls.collection.insert_one(instance.to_native(context={'app_data': {'bson': True}}))
        if result.inserted_id:
            return instance
        raise error.InvalidError('insert to mongo fail')

    def save(self, validate=True):
        if validate:
            self.validate()

        to_set = self.to_native(context={'app_data': {'bson': True}})
        result = self.collection.update_one({'_id': self._id}, {
            '$set': to_set
        }, upsert=True)
        if result.upserted_id or result.matched_count:
            return True
        else:
            raise error.InvalidError('save new model:%s instance fail' % self.__class__.__name__)

    def update(self, payload):
        self.import_data(payload)
        return self.save()

    def refresh(self):
        native = self.collection.find_one({'_id': self._id})
        if not native:
            return False
        self.import_data(native)
        return True
