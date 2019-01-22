#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from patientMatcher import create_app
from patientMatcher.cli.commands import cli
from patientMatcher.utils.add import load_demo

app = create_app()

def test_appname():
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['appname'])
    assert result.output == 'patientMatcher\n'


def test_cli_testconnect(database):
    app.db = database
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['testconnect'])
    assert 'Testing connection' in result.output


def test_cli_add_node(database, test_node):

    app.db = database
    # make sure that "nodes" collection is empty
    assert database['nodes'].find().count() == 0

    # test add a server using the app cli
    runner = app.test_cli_runner()
    result =  runner.invoke(cli, ['add', 'node', '-id', test_node['_id'],
        '-token', test_node['auth_token'], '-matching_url', test_node['matching_url'],
        '-accepted_content', test_node['accepted_content']])
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database['nodes'].find().count() == 1


def test_cli_add_client(database, test_client):

    app.db = database
    # make sure that "nodes" collection is empty
    assert database['client'].find().count() == 0

    # test add a server using the app cli
    runner = app.test_cli_runner()
    result =  runner.invoke(cli, ['add', 'client', '-id', test_client['_id'],
        '-token', test_client['auth_token'], '-url', test_client['base_url']])
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database['clients'].find().count() == 1


def test_cli_add_demo_data(database):
    app.db = database
    runner = app.test_cli_runner()

    # make sure that "patients" collection is empty
    assert database['patients'].find().count() == 0

    # run the load demo command without the -compute_phenotypes flag
    result =  runner.invoke(cli, ['add', 'demodata', '-no_monarch_phenotypes'])
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

    # test that without a valid id or label no patient is removed
    result =  runner.invoke(cli, ['remove', 'patient', '-id', '', '-label', ''])
    assert 'Error' in result.output

    # involke cli command to remove the patient by id and label
    result =  runner.invoke(cli, ['remove', 'patient', '-id', inserted_id, '-label', 'Patient number 1'])
    assert result.exit_code == 0

    # check that the patient was removed from database
    assert database['patients'].find().count() == 0
