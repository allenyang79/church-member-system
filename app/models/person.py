# -*- coding: utf-8 -*-

from schematics.models import Model
from schematics.types import StringType, IntType, BooleanType, ListType, ModelType
from custom_types import MongoDateType

from app.db import db
from app import error
from app.models.utils import get_increment_id

from app.models import DocumentModel
from app.models import CollectionProperty


class PersonRelationModel(Model):
    person_id = IntType(required=True)
    rels = ListType(StringType)


class PersonEventModel(Model):
    date = MongoDateType(required=True)
    description = StringType(required=True)


class GroupMemberModel(Model):
    group_id = IntType(required=True)
    titles = ListType(StringType)


class PersonModel(DocumentModel):
    collection = CollectionProperty('persons')

    person_id = IntType()

    name = StringType()
    social_id = StringType()

    gender = StringType(choices=['male', 'female'])
    birthday = MongoDateType()

    phone_0 = StringType()
    phone_1 = StringType()
    phone_2 = StringType()

    address_0 = StringType()
    address_1 = StringType()

    email_0 = StringType()
    email_1 = StringType()

    education = StringType()
    job = StringType()

    is_register = BooleanType(default=lambda: False)
    register_date = MongoDateType()
    unregister_date = MongoDateType()

    baptize_date = MongoDateType()
    baptize_priest = StringType()

    gifts = ListType(StringType)
    events = ListType(ModelType(PersonEventModel), default=lambda: [], serialize_when_none=True)
    relations = ListType(ModelType(PersonRelationModel), default=lambda: [], serialize_when_none=True)

    groups = ListType(ModelType(GroupMemberModel), default=lambda: [], serialize_when_none=True)

    note = StringType()
    removed = BooleanType(default=False, serialize_when_none=True)

    @classmethod
    def create(cls, payload):
        instance = cls(payload)
        instance.person_id = get_increment_id(cls.collection.name)
        instance.validate()
        result = cls.collection.insert_one(instance.to_native(context={'app_data': {'bson': True}}))
        if result.inserted_id:
            return instance
        raise error.InvalidError('insert to mongo fail')

    @classmethod
    def get_one(cls, person_id):
        return super(cls, cls).get_one('person_id', person_id)

    @classmethod
    def search(cls, term=None):
        query = {
            'removed': {'$ne': True}
        }
        if term:
            query.setdefault('$or', [])
            query['$or'].append({
                'name': {'$regex': term, '$options': 'i'}
            })

        return cls.fetch(query)

    @classmethod
    def fetch_names(cls):
        projected_fields = {
            '_id': False,
            'person_id': True,
            'name': True
        }
        return list(cls.collection.find({}, projected_fields))

    def save(self, validate=True):
        return super(PersonModel, self).save()

    def remove(self):
        self.removed = True
        self.save()

        self.update_relations([])
        return True

    def add_relation(self, person_rel, both=False):
        person_rel = PersonRelationModel(person_rel)

        if self.person_id == person_rel.person_id:
            raise error.InvalidError('can not build relation with self')

        other_person = self.__class__.get_one(person_rel.person_id)
        if not other_person:
            raise error.InvalidError('not existed for build')

        person_rel.rels = sorted(person_rel.rels)
        relations = {person_rel.person_id: person_rel for person_rel in self.relations}
        relations[person_rel.person_id] = person_rel
        self.relations = sorted(relations.values(), key=lambda person_rel: person_rel.person_id)
        self.save()

        if both:
            other_person.add_relation(PersonRelationModel({
                'person_id': self.person_id,
                'rels': person_rel.rels
            }))
        return True

    def remove_relation(self, other_person_id, both=False):
        relations = {person_rel.person_id: person_rel for person_rel in self.relations}
        if other_person_id in relations:
            del relations[other_person_id]
        self.relations = sorted(relations.values(), key=lambda person_rel: person_rel.person_id)
        self.save()

        if both:
            other_person = PersonModel.get_one(other_person_id)
            if other_person:
                other_person.remove_relation(self.person_id)
        return True

    def update_relations(self, person_rels):
        add_person_ids = set(person_rel.person_id for person_rel in person_rels)
        remove_preson_ids = set(person_rel.person_id for person_rel in self.relations) - add_person_ids
        add_person_ids, [pr.person_id for pr in self.relations]

        for person_rel in person_rels:
            self.add_relation(person_rel, both=True)
        for person_id in remove_preson_ids:
            self.remove_relation(person_id, both=True)
        return True



