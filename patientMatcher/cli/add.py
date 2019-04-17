#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import datetime
from flask.cli import with_appcontext, current_app

from patientMatcher.resources import path_to_benchmark_patients
from patientMatcher.utils.add import load_demo, add_node

@click.group()
def add():
    """Add items to database using the CLI"""
    pass

@add.command()
@click.option('-id', type=click.STRING, nargs=1, required=True, help="Server ID")
@click.option('-label', type=click.STRING, nargs=1, required=True, help="Server Description")
@click.option('-token', type=click.STRING, nargs=1, required=True, help="Authorization token")
@click.option('-matching_url', type=click.STRING, nargs=1, required=True, help="URL to send match requests to")
@click.option('-accepted_content', type=click.STRING, nargs=1, required=True, help="Accepted Content-Type", default="application/vnd.ga4gh.matchmaker.v1.0+json")
@click.option('-contact', type=click.STRING, nargs=1, required=False, help="An email address")
@with_appcontext
def node(id, label, token, matching_url, accepted_content, contact=None):
    """Adds a new server to database"""
    click.echo("Adding a new MatchMaker node to database")
    node_obj = {
        '_id' : id,
        'label' : label,
        'created' : datetime.datetime.now(),
        'auth_token' : token,
        'matching_url' : matching_url,
        'accepted_content' : accepted_content,
        'contact' : contact
    }
    inserted_id, collection = add_node(mongo_db=current_app.db, obj=node_obj, is_client=False)
    if inserted_id:
        click.echo('Inserted node with ID "{}" into database collection {}'.format(inserted_id, collection))
    else:
        click.echo('Aborted')

@add.command()
@click.option('-id', type=click.STRING, nargs=1, required=True, help="Client ID")
@click.option('-token', type=click.STRING, nargs=1, required=True, help="Authorization token")
@click.option('-url', type=click.STRING, nargs=1, required=True, help="Client URL")
@click.option('-contact', type=click.STRING, nargs=1, required=False, help="Client email")
@with_appcontext
def client(id, token, url, contact=None):
    """Adds a new client to database"""
    click.echo("Adding a new client to database")
    client_obj = {
        '_id' : id,
        'created' : datetime.datetime.now(),
        'auth_token' : token,
        'base_url' : url,
        'contact' : contact
    }
    inserted_id, collection = add_node(mongo_db=current_app.db, obj=client_obj, is_client=True)
    if inserted_id:
        click.echo('Inserted client with ID "{}" into database collection {}'.format(inserted_id, collection))
    else:
        click.echo('Aborted')



@add.command()
@with_appcontext
def demodata():
    """Adds a set of 50 demo patients to database"""
    click.echo('Adding 50 test patients to database..')
    inserted_ids = load_demo(path_to_json_data=path_to_benchmark_patients, mongo_db=current_app.db,
        host=current_app.config.get('MME_HOST'))
    click.echo('inserted {} patients into db'.format(len(inserted_ids)))


add.add_command(node)
add.add_command(client)
add.add_command(demodata)
