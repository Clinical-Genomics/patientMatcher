#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import click
from flask.cli import FlaskGroup
from patientMatcher import create_app

LOG = logging.getLogger(__name__)

app = create_app()
cli = FlaskGroup(create_app=create_app)

@cli.command()
def test_connection():
    """Retrieves the names of all collection in db"""
    collections = app.db.collection_names()
    LOG.info('Collections in database: {}'.format(collections))

if __name__ == '__main__':
    cli()
