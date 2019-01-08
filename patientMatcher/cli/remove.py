#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from flask.cli import with_appcontext, current_app

from patientMatcher.utils.delete import delete_by_query

@click.group()
def remove():
    """Remove items from database using the CLI"""
    pass

@remove.command()
@click.option('-id', type=click.STRING, nargs=1, required=False, help="ID of the patient to be removed from database")
@click.option('-label', type=click.STRING, nargs=1, required=False, help="ID of the patient to be removed from database")
@with_appcontext
def patient(id, label):
    """Removing a patient from patientMatcher providing its ID"""

    if not id and not label:
        click.echo('Error: either ID and/or label should be provided to delete a patient.')
        raise click.Abort()
    query = {}
    if id:
        query['_id'] = id
    if label:
        query['label'] = label

    n_removed = delete_by_query(query=query, mongo_db= current_app.db, mongo_collection='patients')
    click.echo('Number of patients removed from database:{}'.format(n_removed))
