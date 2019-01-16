#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import click
from flask.cli import with_appcontext, current_app

from patientMatcher.utils.add import load_demo, add_node

@click.group()
def add():
    """Add items to database using the CLI"""
    pass

@add.command()
@click.option('-id', type=click.STRING, nargs=1, required=True, help="Server/Client ID")
@click.option('-token', type=click.STRING, nargs=1, required=True, help="Authorization token")
@click.option('-is_client', is_flag=True, default=False, help='If True the node is a client of patientMatcher')
@click.option('-url', type=click.STRING, nargs=1, required=True, help="Server/client URL")
@click.option('-contact', type=click.STRING, nargs=1, required=False, help="An email address")
@with_appcontext
def node(is_client, id, token, url, contact=None):
    """Registers a new client/server to database"""
    click.echo("Adding new node to database. Is node client: {}".format(is_client))
    inserted_id, collection = add_node(mongo_db=current_app.db, id=id, token=token, is_client=is_client, url=url, contact=contact)
    if inserted_id:
        click.echo('Inserted node with ID "{}" into database collection {}'.format(inserted_id, collection))
    else:
        click.echo('Aborted')


@add.command()
@click.option('-compute_phenotypes', is_flag=True, default=False, help='compute phenotypes from HPO terms')
@with_appcontext
def demo_patients(compute_phenotypes):
    """Adds a set of 50 demo patients to database"""
    #click.echo('Adding 50 test patients to database..')

    path_to_json_patients = os.path.abspath(os.path.join(current_app.root_path, 'resources', 'benchmark_patients.json'))
    click.echo(path_to_json_patients)
    inserted_ids = load_demo(path_to_json_data=path_to_json_patients, mongo_db=current_app.db, compute_phenotypes=compute_phenotypes)

    click.echo('inserted {} patients into db'.format(len(inserted_ids)))
    click.echo(inserted_ids)

add.add_command(node)
add.add_command(demo_patients)
