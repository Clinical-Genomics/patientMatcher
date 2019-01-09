#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from flask.cli import FlaskGroup
from flask.cli import with_appcontext, current_app
from patientMatcher import create_app
from .add import add
from .remove import remove

from patientMatcher.match.genotype_matcher import match  # --------->>>>>>> REMOVE!!!!!!!!

cli = FlaskGroup(create_app=create_app)

@cli.command()
@with_appcontext
def test_connection():
    """Retrieves the names of all collections in db"""
    collections = current_app.db.collection_names()
    click.echo('Collections in database: {}'.format(collections))
    return collections


@cli.command()
@with_appcontext
def test_matching():
    max_gt_score = current_app.config['MAX_GT_SCORE']
    match(current_app.db, max_gt_score)


cli.add_command(add)
cli.add_command(remove)
