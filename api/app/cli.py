# -*- coding: utf-8 -*-
import sys
import argparse
import click

from app.db import init_db
from app.models import AdminModel

@click.group(chain=True)
def cli():
    pass


@cli.command('create_admin')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--role', prompt=True, type=click.Choice(['ROOT', 'ADMIN', 'VIEWER']))
def create_admin(username, password, role):
    """
    create a admin. if admin's username is not existed.
    """
    username = username.lower()
    admin = AdminModel.get_one(username)
    if admin:
        print 'error!! `%s` is existed.' % username
        sys.exit()
    roles = []
    if role:
        roles.append(role)
    admin = AdminModel.create(username, password, roles=roles)
    print 'create admin success.'

@cli.command('reset_admin_password')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def reset_admin_password(username, password):
    """
    reset a admin's password.
    """
    username = username.lower()
    admin = AdminModel.get_one(username)
    if not admin:
        print 'error!! `%s` is not existed.' % username
        sys.exit()
    admin.update_password(password)
    print 'update success.'


@cli.command('init_database')
def init_database():
    """"build index of database."""
    init_db()
    print 'init database success'

if __name__ == '__main__':
    cli()
