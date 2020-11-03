#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from flask_mail import Message

from patientMatcher.cli.commands import cli
from patientMatcher.parse.patient import mme_patient


def test_appname(mock_app):
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, ["test", "name"])
    assert result.output == "patientMatcher\n"


def test_sendemail(mock_app, mock_mail):
    mock_app.mail = mock_mail
    mock_app.config["MAIL_USERNAME"] = "sender@email.com"

    runner = mock_app.test_cli_runner()
    # When invoking the test email command with a recipient paramrter
    result = runner.invoke(cli, ["test", "email", "-recipient", "test_user@mail.com"])

    # Make sure that mock mail send method was called and mock email is sent
    assert mock_mail._send_was_called
    assert mock_mail._message
    assert "Mail correctly sent" in result.output


def test_cli_add_node(mock_app, database, test_node):
    # make sure that "nodes" collection is empty
    assert database["nodes"].find_one() is None

    # test add a server using the app cli
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli,
        [
            "add",
            "node",
            "-id",
            test_node["_id"],
            "-label",
            "This is a test node",
            "-token",
            test_node["auth_token"],
            "-matching_url",
            test_node["matching_url"],
            "-accepted_content",
            test_node["accepted_content"],
        ],
    )
    assert result.exit_code == 0
    assert "Inserted node" in result.output

    # check that the server was added to the "nodes" collection
    assert database["nodes"].find_one()

    # Try adding the node again
    result = runner.invoke(
        cli,
        [
            "add",
            "node",
            "-id",
            test_node["_id"],
            "-label",
            "This is a test node",
            "-token",
            test_node["auth_token"],
            "-matching_url",
            test_node["matching_url"],
            "-accepted_content",
            test_node["accepted_content"],
        ],
    )
    assert result.exit_code == 0
    # And you should get an abort message
    assert "Aborted" in result.output
    # And number of nodes in database should stay the same
    results = database["nodes"].find()
    assert len(list(results)) == 1


def test_cli_add_client(mock_app, database, test_client):

    # make sure that "clients" collection is empty
    assert database["client"].find_one() is None

    # test add a server using the app cli
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli,
        [
            "add",
            "client",
            "-id",
            test_client["_id"],
            "-token",
            test_client["auth_token"],
            "-url",
            test_client["base_url"],
        ],
    )

    assert result.exit_code == 0
    assert "Inserted client" in result.output

    # check that the server was added to the "nodes" collection
    assert database["clients"].find_one()

    # Try adding the client again
    result = runner.invoke(
        cli,
        [
            "add",
            "client",
            "-id",
            test_client["_id"],
            "-token",
            test_client["auth_token"],
            "-url",
            test_client["base_url"],
        ],
    )
    assert result.exit_code == 0
    # And you should get an abort message
    assert "Aborted" in result.output
    # And number of clients in database should stay the same
    results = database["clients"].find()
    assert len(list(results)) == 1


def test_cli_remove_client(mock_app, database, test_client):

    # Add a client to database
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli,
        [
            "add",
            "client",
            "-id",
            test_client["_id"],
            "-token",
            test_client["auth_token"],
            "-url",
            test_client["base_url"],
        ],
    )
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database["clients"].find_one()

    # Use the cli to remove client
    result = runner.invoke(cli, ["remove", "client", "-id", test_client["_id"]])

    # check that command is executed withour errors
    assert result.exit_code == 0

    # and that client is gone from database
    assert database["clients"].find_one() is None


def test_cli_remove_node(mock_app, database, test_node):

    # Add a node to database
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli,
        [
            "add",
            "node",
            "-id",
            test_node["_id"],
            "-label",
            "This is a test node",
            "-token",
            test_node["auth_token"],
            "-matching_url",
            test_node["matching_url"],
            "-accepted_content",
            test_node["accepted_content"],
        ],
    )
    assert result.exit_code == 0

    # check that the server was added to the "nodes" collection
    assert database["nodes"].find_one()

    # Use the cli to remove client
    result = runner.invoke(cli, ["remove", "node", "-id", test_node["_id"]])

    # check that command is executed withour errors
    assert result.exit_code == 0

    # and that node is gone from database
    assert database["nodes"].find_one() is None


def test_cli_update_resources(mock_app):

    runner = mock_app.test_cli_runner()

    # run resources update command with --test flag:
    result = runner.invoke(cli, ["update", "resources"])
    assert result.exit_code == 0


def test_cli_add_demo_data(mock_app, database):

    runner = mock_app.test_cli_runner()

    # make sure that "patients" collection is empty
    assert database["patients"].find_one() is None

    # run the load demo command without the -compute_phenotypes flag
    result = runner.invoke(cli, ["add", "demodata"])
    assert result.exit_code == 0

    # check that the 50 demo patients where inserted into database
    results = database["patients"].find()
    assert len(list(results)) == 50


def test_cli_remove_patient(mock_app, database, gpx4_patients, match_objs):

    runner = mock_app.test_cli_runner()

    # add a test patient to database
    test_patient = mme_patient(gpx4_patients[0], True)  # True --> convert gene symbols to ensembl
    inserted_id = mock_app.db["patients"].insert_one(test_patient).inserted_id
    assert inserted_id == gpx4_patients[0]["id"]

    # there is now 1 patient in database
    assert database["patients"].find_one()

    # test that without a valid id or label no patient is removed
    result = runner.invoke(cli, ["remove", "patient", "-id", "", "-label", ""])
    assert "Error" in result.output

    # Add mock patient matches objects to database
    database["matches"].insert_many(match_objs)
    # There should be 2 matches in database for this patient:
    results = database["matches"].find({"data.patient.id": inserted_id})
    assert len(list(results)) == 2

    # involke cli command to remove the patient by id and label
    result = runner.invoke(
        cli, ["remove", "patient", "-id", inserted_id, "-label", "350_1-test", "-leave_matches"]
    )
    assert result.exit_code == 0

    # check that the patient was removed from database
    assert database["patients"].find_one() is None

    # But matches are still there
    results = database["matches"].find({"data.patient.id": inserted_id})
    assert len(list(results)) == 2

    # Run remove patient command with option to remove matches but without patient ID
    result = runner.invoke(cli, ["remove", "patient", "-label", "350_1-test", "-remove_matches"])
    # And make sure that it doesn't work
    assert "Please provide patient ID and not label to remove all its matches." in result.output

    # Test now the proper command to remove patient matches:
    result = runner.invoke(cli, ["remove", "patient", "-id", inserted_id, "-remove_matches"])
    assert result.exit_code == 0

    # And make sure that patient removal removed its matchings
    assert database["matches"].find_one({"data.patient.id": inserted_id}) is None
