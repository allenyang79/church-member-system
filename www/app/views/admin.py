# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
from app import auth
from app import error
from app.permissions import PERMISSIONS
from app.models import AdminModel


blueprint = Blueprint('admin', __name__)


@blueprint.route('/admin/list')
def admin_list():
    me = auth.me()
    if me.has_permissions(PERMISSIONS.READ_ADMIN):
        query = {}
    else:
        query = {'username': me.username}
    return {
        'success': True,
        'data': [admin.as_dict() for admin in AdminModel.fetch(query)]
    }


@blueprint.route('/admin/create', methods=['POST'])
def admin_create():
    if not auth.me().has_permissions(PERMISSIONS.WRITE_ADMIN):
        raise error.AccessDenyError()

    payload = request.get_json()
    AdminModel.create(payload.get('username'), payload.get('password'))
    return {
        'success': True,
        'data': {}
    }


@blueprint.route('/admin/one/<string:username>/update', methods=['POST'])
def admin_one_update(username):


    payload = request.get_json()
    admin = AdminModel.get_one(username)
    if not admin:
        raise error.InvalidError('`%s` is not existed' % username)

    if not auth.me().can_modify(admin):
        raise error.AccessDenyError()

    fields = ('name', 'description')
    if auth.me().has_permissions(PERMISSIONS.WRITE_ADMIN):
        fields += ('roles',)
        if not admin.has_permissions(PERMISSIONS.ROOT):
            fields += ('enabled',)
    for field in fields:
        if field in payload:
            setattr(admin, field, payload[field])
    admin.save()
    return {
        'success': True,
        'data': admin.as_dict()
    }


@blueprint.route('/admin/one/<string:username>/update_password', methods=['POST'])
def admin_one_update_password(username):
    payload = request.get_json()

    admin = AdminModel.get_one(username)

    if not admin:
        raise error.InvalidError('`%s` is not existed' % username)

    if not auth.me().can_modify(admin):
        raise error.AccessDenyError()

    if not payload.get('new_password'):
        raise error.InvalidError('`new_password` is required.')

    return {
        'success': admin.update_password(payload['new_password'])
    }


@blueprint.route('/admin/me')
def admin_me():
    return auth.me().as_dict()


