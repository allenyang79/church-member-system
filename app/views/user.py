# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import request
from app import auth
from app.models import AdminModel


""" User
"""

blueprint = Blueprint('user', __name__)


