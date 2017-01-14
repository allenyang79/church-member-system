# -*- coding: utf-8 -*-

import datetime
import os
import sys
import json
import bson
import bson.objectid

from app.config import config
from app.db import db
from app.main import init_app
from app.models import PersonModel, GroupModel
from app.models import GroupMember

import unittest


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.app = init_app()
        self.app.debug = True
        self.client = self.app.test_client()

        # login
        payload = {
            'username': config.get('auth', 'DEFAULT_ADMIN_USERNAME'),
            'password': config.get('auth', 'DEFAULT_ADMIN_PASSWORD')
        }
        r = self.client.post('/login', data=json.dumps(payload), content_type='application/json')

    def tearDown(self):
        db.persons.delete_many({})
        db.groups.delete_many({})

    def test_person_one(self):
        person = PersonModel({
            'name': 'person_name'
        })
        person.save()

        r = self.client.get('/person/one/%s' % person._id)
        result = json.loads(r.data)['data']
        self.assertEqual(person.to_primitive(), result)

    def test_person_create(self):
        post = {
            'name': 'person_name'
        }
        r = self.client.post('/person/create', data=json.dumps(post), content_type='application/json')
        result = json.loads(r.data)
        self.assertEqual(post['name'], result['data']['name'])

    def test_person_update(self):
        person = PersonModel({
            'name': 'person_name'
        })
        person.save()

        post = {
            'name': 'person_name_update'
        }
        r = self.client.post('/person/one/%s/update' % person._id, data=json.dumps(post), content_type='application/json')
        result = json.loads(r.data)
        self.assertEqual(post['name'], result['data']['name'])

    def test_person_list(self):
        rows = []
        for i in range(0, 3):
            person = PersonModel({
                'name': 'person_name_%s' % i
            })
            person.save()
            rows.append(person)

        r = self.client.get('/person/list')
        result = json.loads(r.data)
        self.assertEqual(len(result['data']), len(rows))

    def test_person_realtion(self):
        persons = []
        for i in range(0, 3):
            person = PersonModel({
                'name': 'person_name_%s' % i
            })
            person.save()
            persons.append(person)

        post = [
            {'person_id': str(persons[1]._id), 'rels': ['family']},
        ]
        r = self.client.post('/person/one/%s/relation' % persons[0]._id, data=json.dumps(post), content_type='application/json')

        p0 = PersonModel.get_one(persons[0]._id)
        p1 = PersonModel.get_one(persons[1]._id)
        self.assertEqual(p0.relations[0].person_id, p1._id)
        self.assertEqual(p1.relations[0].person_id, p0._id)

        post = [
            {'person_id': str(persons[0]._id), 'rels': ['family']},
            {'person_id': str(persons[2]._id), 'rels': ['family']},
        ]
        r = self.client.post('/person/one/%s/relation' % persons[1]._id, data=json.dumps(post), content_type='application/json')
        p1 = PersonModel.get_one(persons[1]._id)
        self.assertEqual(len(p1.relations), 2)

        post = []
        r = self.client.post('/person/one/%s/relation' % persons[0]._id, data=json.dumps(post), content_type='application/json')
        p0 = PersonModel.get_one(persons[0]._id)
        self.assertEqual(len(p0.relations), 0)


    def test_person_remove(self):
        person = PersonModel({
            'name': 'person_name'
        })
        person.save()

        r = self.client.post('/person/one/%s/remove' % person._id, data=json.dumps({}), content_type='application/json')
        person = PersonModel.get_one(person._id)
        self.assertEqual(person.removed, True)

    def test_person_names(self):
        persons = []
        for i in range(0, 3):
            person = PersonModel({
                'name': 'person_name_%s' % i
            })
            person.save()
            persons.append(person)

        r = self.client.get('/person/names')
        result = json.loads(r.data)
        self.assertItemsEqual([str(x._id) for x in persons], [x['_id'] for x in result['data']])
        self.assertItemsEqual([x.name for x in persons], [x['name'] for x in result['data']])

    def test_group_create(self):
        group = GroupModel({
            'name': 'group_name'
        })
        r = self.client.post('/group/create', data=json.dumps(group.to_primitive()), content_type='application/json')
        _group = GroupModel.get_one(group._id)
        self.assertEqual(group._id, _group._id)
        self.assertEqual(group, _group)

    def test_group_update(self):
        group = GroupModel.create({
            'name': 'group_name'
        })

        person_id = str(bson.objectid.ObjectId())
        post = {
            'note': 'this is group note',
            'members': [{'person_id': person_id, 'title': 'anytitle'}]
        }
        r = self.client.post('/group/one/%s/update' % group._id, data=json.dumps(post), content_type='application/json')
        _group = GroupModel.get_one(group._id)
        self.assertEqual(_group._id, group._id)
        self.assertEqual(_group.note, post['note'])
        self.assertEqual(_group.members, [GroupMember({'person_id': person_id, 'title': 'anytitle'})])

    def test_group_members(self):
        persons = []
        for i in range(0, 3):
            person = PersonModel({
                'name': 'person_name_%s' % i
            })
            person.save()
            persons.append(person)
        group = GroupModel.create({
            'name': 'group_name',
            'members': [{
                'person_id': persons[0]._id,
                'title': 'title_0'
            },{
                'person_id': persons[1]._id,
                'title': 'title_1'

            },]
        })
        r = self.client.get('/group/one/%s/member' % group._id)
        result = json.loads(r.data)
        self.assertItemsEqual(result['data'], [{
            'person_id': str(persons[0]._id),
            'title': 'title_0',
            'name': 'person_name_0'
        },{
            'person_id': str(persons[1]._id),
            'title': 'title_1',
            'name': 'person_name_1'
        }])

