# -*- coding: utf-8 -*-

from flask import Blueprint  # , render_template, abort
from flask import request

from app import auth
from app.logger import logger
from app.error import InvalidError

from app.models import PersonModel
from app.models import GroupModel

######################
#   group
######################

blueprint = Blueprint('group', __name__)

@blueprint.route('/group/create', methods=['POST'])
def group_create():
    payload = request.get_json()
    group = GroupModel.create(payload)
    return {
        'success': True,
        'data': group.to_primitive()
    }


@blueprint.route('/group/one/<int:group_id>')
def group_one(group_id):
    group = GroupModel.get_one(group_id)
    if not group:
        raise InvalidError('Group(%s) is not existed.' % group_id)
    return {
        'success': True,
        'data': group.to_primitive()
    }


@blueprint.route('/group/list')
def group_list():
    groups = GroupModel.fetch()
    return {
        'success': True,
        'data': [group.to_primitive() for group in groups],
    }


@blueprint.route('/group/one/<int:group_id>/update', methods=['POST'])
def group_one_update(group_id):
    group = GroupModel.get_one(group_id)
    if not group:
        raise InvalidError('Group(%s) is not existed.' % group_id)

    payload = request.get_json()
    group.update(payload)

    return {
        'success': True,
        'data': group.to_primitive()
    }


@blueprint.route('/group/one/<int:group_id>/member')
def group_member(group_id):
    group = GroupModel.get_one(group_id)
    if not group:
        raise InvalidError('Group(%s) is not existed.' % _id)
    return {
        'success': True,
        'data': [p.to_primitive() for p in group.get_members()]
    }


