#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from patientMatcher import create_app
from patientMatcher.cli.commands import cli
from patientMatcher.utils.add import load_demo

app = create_app()

def test_baseapp():
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['appname'])
    assert result.output == 'patientMatcher\n'


def test_cli_connection(database):
    app.db = database
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['test_connection'])
    #assert 'Testing connection' in result.output


def test_cli_add_node(database, demo_node):
    app.db = database

    # make sure that "nodes" collection is empty
    assert database['nodes'].find().count() == 0

    # add a server using the app cli
    server = demo_node
    runner = app.test_cli_runner()
    result =  runner.invoke(cli, ['add', 'node', '-id', server['_id'],
        '-token', server['auth_token'], '-url', server['base_url']])
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database['nodes'].find().count() == 1


def test_cli_add_demo_data(database):
    app.db = database
    runner = app.test_cli_runner()

    # make sure that "patients" collection is empty
    assert database['patients'].find().count() == 0

    # run the load demo command without the -compute_phenotypes flag
    result =  runner.invoke(cli, ['add', 'demo_patients', '-no_monarch_phenotypes'])
    assert result.exit_code == 0

    # check that the 50 demo patients where inserted into database
    assert database['patients'].find().count() == 50


def test_cli_remove_patient(database, json_patients):
    app.db = database
    runner = app.test_cli_runner()

    # add a test patient to database
    test_patient = json_patients[0]
    test_patient['_id'] = 'test_id'
    inserted_id = app.db['patients'].insert_one(test_patient).inserted_id
    assert inserted_id == 'test_id'

    # there is now 1 patient in database
    assert database['patients'].find().count() == 1

    # involke cli command to remove the patient
    result =  runner.invoke(cli, ['remove', 'patient', '-id', inserted_id])
    assert result.exit_code == 0

    # check that the patient was removed from database
    assert database['patients'].find().count() == 0
