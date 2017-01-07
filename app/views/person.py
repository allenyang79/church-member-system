# -*- coding: utf-8 -*-
import re

from flask import Blueprint  # , render_template, abort
from flask import request

from app import auth
from app.logger import logger
from app.error import InvalidError

from app.models import PersonModel, PersonRelationModel
from app.models import GroupModel

blueprint = Blueprint('person', __name__)

""" Person
"""
@blueprint.route('/person/one/<int:person_id>')
def person_one(person_id):
    person = PersonModel.get_one(person_id)
    if not person:
        raise InvalidError('person(%s) is not existed' % person_id)

    return {
        'success': True,
        'data': person.to_primitive()
    }


@blueprint.route('/person/list')
def person_list():
    term = request.values.get('term')
    return {
        'success': True,
        'data': [person.to_primitive() for person in PersonModel.search(term)],
    }


@blueprint.route('/person/create', methods=['POST'])
def person_create():
    payload = request.get_json()
    person = PersonModel.create(payload)
    return {
        'success': True,
        'data': person.to_primitive()
    }


@blueprint.route('/person/one/<int:person_id>/update', methods=['POST'])
def person_one_update(person_id):
    person = PersonModel.get_one(person_id)

    payload = request.get_json()
    allow_field = (
        'name',
        'social_id',
        'gender',
        'birthday',
        'phone_0',
        'phone_1',
        'phone_2',
        'address_0',
        'address_1',
        'email_0',
        'email_1',
        'education',
        'job',
        'is_register',
        'register_day',
        'unregister_day',
        'baptize_date',
        'baptize_priest',
        'gifts',
        'events',
        'groups',
        'note'
    )

    payload = {k: v for k, v in payload.items() if k in allow_field}
    person.update(payload)

    return {
        'success': True,
        'data': person.to_primitive()
    }


@blueprint.route('/person/one/<int:person_id>/relation', methods=['POST'])
def person_update_relation(person_id):
    person = PersonModel.get_one(person_id)
    if not person:
        raise InvalidError('Person(%s) is not existed.' % person_id)

    payload = request.get_json()
    relations = [PersonRelationModel(x) for x in payload.get('relations', [])]
    person.update_relations(relations)

    return {'success': True}


@blueprint.route('/person/one/<int:person_id>/relation')
def person_relation(person_id):
    query = {
        'relations.person_id': person_id,
        'removed': False
    }
    data = [p.to_primitive() for p in PersonModel.fetch(query)]
    return {'success': True, 'data': data}


@blueprint.route('/person/one/<int:person_id>/remove', methods=['POST'])
def person_remove(person_id):
    person = PersonModel.get_one(person_id)
    if not person:
        raise InvalidError('Person(%s) is not existed.' % person_id)
    person.remove()
    return {'success': True}


@blueprint.route('/person/names')
def person_names():
    return {
        'success': True,
        'data': PersonModel.fetch_names()
    }
    #result = [p.to_primitive() for p in PersonModel.fetch(query={}, fields=('person_id', 'name'))]
    #return {'success': True, 'data': result}


