#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import pymongo
from flask.cli import FlaskGroup, with_appcontext
from patientMatcher import create_app
from .add import add
from .remove import remove

cli = FlaskGroup(create_app=create_app)

@cli.command()
@with_appcontext
def appname():
    """Returns the app name, for testing purposes, mostly"""
    click.echo(current_app.name)


@cli.command()
@with_appcontext
def testconnect():
    """Retrieves the names of all collections in db"""
    collections = current_app.db.collection_names()
    click.echo('Testing connection. Collections in database: {}'.format(collections))


cli.add_command(add)
cli.add_command(remove)
