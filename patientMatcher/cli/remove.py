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
@click.option('-label', type=click.STRING, nargs=1, required=False, help="Label of the patient to be removed from database")
@click.option('-remove_matches/-leave_matches', default=False, help="Remove or leave on db matches triggered by patient")
@with_appcontext
def patient(id, label, remove_matches):
    """Removing a patient from patientMatcher providing its ID"""

    if not id and not label:
        click.echo('Error: either ID and/or label should be provided to delete a patient.')
        raise click.Abort()

    if remove_matches and not id:
        click.echo('Please provide patient ID and not label to remove all its matches.')
        raise click.Abort()

    query = {}
    if id:
        query['_id'] = id
    if label:
        query['label'] = label

    n_removed = delete_by_query(query=query, mongo_db= current_app.db, mongo_collection='patients')
    click.echo('Number of patients removed from database:{}'.format(n_removed))

    if remove_matches:
        # this will remove ONLY matches where this patient was the query patient
        # NOT those where patient was among the matching results
        query = {'data.patient.id' : id}
        n_removed = delete_by_query(query=query, mongo_db= current_app.db, mongo_collection='matches')
        click.echo('Number of matches for this patient removed from database:{}'.format(n_removed))


@remove.command()
@click.option('-id', type=click.STRING, nargs=1, required=True, help="ID of the client to be removed from database")
@with_appcontext
def client(id):
    """Remove a client from database by providing its ID"""

    query = {'_id' : id}
    n_removed = delete_by_query(query=query, mongo_db= current_app.db, mongo_collection='clients')
    click.echo('Number of clients removed from database:{}'.format(n_removed))


@remove.command()
@click.option('-id', type=click.STRING, nargs=1, required=True, help="ID of the node to be removed from database")
@with_appcontext
def node(id):
    """Remove a node from database by providing its ID"""

    query = {'_id' : id}
    n_removed = delete_by_query(query=query, mongo_db= current_app.db, mongo_collection='nodes')
    click.echo('Number of nodes removed from database:{}'.format(n_removed))
