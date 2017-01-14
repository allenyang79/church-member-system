# -*- coding: utf-8 -*-

from schematics.models import Model
from schematics.types import StringType, IntType, BooleanType, ListType, ModelType
from custom_types import MongoDateType

from app.db import db
from app import error
from app.models.utils import get_increment_id

from app.models import DocumentModel
from app.models import CollectionProperty


class GroupModel(DocumentModel):
    collection = CollectionProperty('groups')

    group_id = IntType()
    name = StringType()
    begin_at = MongoDateType()
    end_at = MongoDateType()
    note = StringType()
    removed = BooleanType(default=False)

    @classmethod
    def create(cls, payload):
        instance = cls(payload)
        instance.group_id = get_increment_id(cls.collection.name)
        instance.validate()
        result = cls.collection.insert_one(instance.to_native(context={'app_data': {'bson': True}}))
        return instance

    @classmethod
    def fetch_names(cls):
        projected_fields = {
            '_id': False,
            'group_id': True,
            'name': True
        }
        return list(cls.collection.find({}, projected_fields))

    @classmethod
    def get_one(cls, group_id):
        return super(cls, cls).get_one('group_id', group_id)

    def get_members(self):
        persons = db.persons.find({
            'groups.group_id': self.group_id
        })
        return map(lambda p: PersonModel(p), persons)

    def add_member(self, person_id, titles):
        person = PersonModel.get_one(person_id)
        gms = {gm.group_id: gm for gm in person.groups}
        gms[self.group_id] = GroupMemberModel({
            'group_id': self.group_id,
            'titles': titles
        })
        person.groups = sorted(gms.values(), key=lambda gm: gm.group_id)
        return person.save()

    def remove_member(self, person_id):
        person = PersonModel.get_one(person_id)
        gms = {gm.group_id: gm for gm in person.groups}
        if self.group_id in self.gms:
            del gms[self.group_id]
        person.groups = sorted(gms.values(), key=lambda gm: gm.group_id)
        return person.save()
