#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from flask_mail import Message

from patientMatcher import create_app
from patientMatcher.cli.commands import cli
from patientMatcher.utils.add import load_demo

app = create_app()

def test_appname():
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['test', 'name'])
    assert result.output == 'patientMatcher\n'


def test_sendemail(mock_mail):
    app.mail = mock_mail
    app.config['MAIL_USERNAME'] = 'sender@email.com'

    runner = app.test_cli_runner()
    # When invoking the test email command with a recipient paramrter
    result = runner.invoke(cli, ['test', 'email', '-recipient', 'test_user@mail.com'])

    # Make sure that mock mail send method was called and mock email is sent
    assert mock_mail._send_was_called
    assert mock_mail._message
    assert 'Mail correctly sent' in result.output


def test_cli_testconnect(database):
    app.db = database
    runner = app.test_cli_runner()
    result = runner.invoke(cli, ['test', 'connection'])
    assert 'Connect test OK: Mongo client is connected' in result.output


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


def test_cli_remove_client(database, test_client):

    app.db = database

    # Add a client to database
    runner = app.test_cli_runner()
    result =  runner.invoke(cli, ['add', 'client', '-id', test_client['_id'],
        '-token', test_client['auth_token'], '-url', test_client['base_url']])
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database['clients'].find().count() == 1

    # Use the cli to remove client
    result =  runner.invoke(cli, ['remove', 'client', '-id', test_client['_id'] ])

    # check that command is executed withour errors
    assert result.exit_code == 0

    # and that client is gone from database
    assert database['clients'].find().count() == 0


def test_cli_remove_node(database, test_node):

    app.db = database

    # Add a node to database
    runner = app.test_cli_runner()
    result =  runner.invoke(cli, ['add', 'node', '-id', test_node['_id'],
        '-token', test_node['auth_token'], '-matching_url', test_node['matching_url'],
        '-accepted_content', test_node['accepted_content']])
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database['nodes'].find().count() == 1

    # Use the cli to remove client
    result =  runner.invoke(cli, ['remove', 'node', '-id', test_node['_id'] ])

    # check that command is executed withour errors
    assert result.exit_code == 0

    # and that node is gone from database
    assert database['nodes'].find().count() == 0


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


def test_cli_remove_patient(database, json_patients, match_objs):
    app.db = database
    runner = app.test_cli_runner()

    # add a test patient to database
    test_patient = json_patients[0]
    test_patient['_id'] = 'P0000079'
    inserted_id = app.db['patients'].insert_one(test_patient).inserted_id
    assert inserted_id == 'P0000079'

    # there is now 1 patient in database
    assert database['patients'].find().count() == 1

    # test that without a valid id or label no patient is removed
    result =  runner.invoke(cli, ['remove', 'patient', '-id', '', '-label', ''])
    assert 'Error' in result.output

    # Add mock patient matches objects to database
    database['matches'].insert_many(match_objs)
    # There should be 2 matches in database for this patient:
    assert database['matches'].find( {'data.patient.id' : inserted_id }).count() == 2

    # involke cli command to remove the patient by id and label
    result =  runner.invoke(cli, ['remove', 'patient', '-id', inserted_id, '-label', 'Patient number 1', '-leave_matches'])
    assert result.exit_code == 0

    # check that the patient was removed from database
    assert database['patients'].find().count() == 0

    # But matches are still there
    assert database['matches'].find( {'data.patient.id' : inserted_id }).count() == 2

    # Run remove patient command with option to remove matches but without patient ID
    result =  runner.invoke(cli, ['remove', 'patient', '-label', 'Patient number 1', '-remove_matches'])
    # And make sure that it doesn't work
    assert 'Please provide patient ID and not label to remove all its matches.' in result.output

    # Test now the proper command to remove patient matches:
    result =  runner.invoke(cli, ['remove', 'patient', '-id', inserted_id, '-remove_matches'])
    assert result.exit_code == 0

    # And make sure that patient removal removed its matchings
    assert database['matches'].find( {'data.patient.id' : inserted_id }).count() == 0
