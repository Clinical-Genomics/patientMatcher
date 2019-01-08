#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import click
from flask.cli import with_appcontext, current_app

from patientMatcher.utils.load import load_demo

@click.group()
def add():
    """Add items to database using the CLI"""
    pass

@add.command()
def node():
    """Adds a new MatchMaker node to database"""
    click.echo('adding a MME node')

@add.command()
@with_appcontext
def demo_patients():
    """Adds a set of 50 demo patients to database"""
    click.echo('Adding 50 test patients to database..')

    path_to_json_patients = os.path.abspath(os.path.join(current_app.root_path, 'resources', 'benchmark_patients.json'))
    inserted_ids = load_demo(path_to_json_data=path_to_json_patients, mongo_db=current_app.db)

    click.echo('inserted {} patients into db'.format(len(inserted_ids)))





add.add_command(node)
add.add_command(demo_patients)
