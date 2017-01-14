# -*- coding: utf-8 -*-
import os
import sys
import datetime
import unittest

from app.config import config
from app.db import db

from app.models import PersonModel
from app.models import PersonRelationModel
from app.models import GroupModel
from app.models import GroupMemberModel


class TestModel(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        db.persons.delete_many({})
        db.groups.delete_many({})
        db.increments.delete_many({})

    def test_person(self):
        person = PersonModel({})

        person.name = 'person_name'
        person.birthday = datetime.datetime.now()
        person.save()

        _person_native = db.persons.find_one({'_id': person._id})
        _person = PersonModel(_person_native)

        for k in person:
            self.assertEqual(person[k], _person[k])
        person.save()

        p1 = PersonModel.create({
            'name': 'Bill',
        })
        self.assertTrue(isinstance(p1.person_id, int))

        p2 = PersonModel.create({
            'name': 'John',
        })
        self.assertEqual(p1.person_id + 1, p2.person_id)

        _p1 = PersonModel.get_one(p1.person_id)
        self.assertEqual(p1, _p1)

        p1.events=[{
            'date': datetime.date.today(),
            'description': 'aaa'
        },{
            'date': datetime.date.today(),
            'description': 'bbb'
        }]
        p1.save()
        p1.refresh()
        self.assertEqual(p1.events[0].date, datetime.date.today())
        self.assertEqual(p1.events[0].description ,'aaa')

        persons = PersonModel.search('bill')
        self.assertEqual(persons[0].person_id, p1.person_id)

    def test_person_relation(self):

        p1 = PersonModel.create({
            'name': 'Bill'
        })

        p2 = PersonModel.create({
            'name': 'John'
        })

        p3 = PersonModel.create({
            'name': 'Mary'
        })

        p1.update_relations([
            PersonRelationModel(dict(person_id=p2.person_id, rels=['brother'])),
            PersonRelationModel(dict(person_id=p3.person_id, rels=['sister'])),
        ])

        self.assertEqual(p1.relations[0].person_id, p2.person_id)
        self.assertEqual(p1.relations[1].person_id, p3.person_id)

        p2.update_relations([
            PersonRelationModel(dict(person_id=p3.person_id, rels=['sister'])),
            PersonRelationModel(dict(person_id=p1.person_id, rels=['brother'])),
        ])

        self.assertEqual(p2.relations[0].person_id, p1.person_id)
        self.assertEqual(p2.relations[1].person_id, p3.person_id)


        p3.refresh()
        p3.update_relations([])

        p1.refresh()
        p2.refresh()
        p3.refresh()

        self.assertEqual(len(p1.relations), 1)
        self.assertEqual(p1.relations[0].person_id, p2.person_id)
        self.assertEqual(len(p2.relations), 1)
        self.assertEqual(p2.relations[0].person_id, p1.person_id)

        self.assertEqual(p3.relations, [])


    def test_group(self):
        """ test group """
        p1 = PersonModel.create({
            'name': 'bill'
        })
        p2 = PersonModel.create({
            'name': 'john'
        })

        g1 = GroupModel.create({
            'name': 'group_01'
        })
        gm = GroupMemberModel({
            'group_id': g1.group_id,
            'titles': ['Boss']
        })

        p1.groups = [GroupMemberModel({
            'group_id': g1.group_id,
            'titles': ['leader', 'boss']
        })]
        p1.save()

        p2.groups = [GroupMemberModel({
            'group_id': g1.group_id,
            'titles': ['accounting', 'member']
        })]
        p2.save()

        self.assertEqual(len(g1.get_members()), 2)

        g2 = GroupModel.create({
            'name': 'group_02',
        })
        g3 = GroupModel.create({
            'name': 'group_03',
        })
        g2.add_member(p1.person_id, ['member'])
        g3.add_member(p1.person_id, ['member'])
        p1.refresh()
        self.assertEqual(p1.groups[0].group_id, g1.group_id)
        self.assertEqual(p1.groups[1].group_id, g2.group_id)
        self.assertEqual(p1.groups[2].group_id, g3.group_id)



