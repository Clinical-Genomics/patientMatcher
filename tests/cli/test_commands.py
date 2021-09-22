#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo
from flask_mail import Message
from patientMatcher.cli.commands import cli
from patientMatcher.parse.patient import mme_patient
from patientMatcher.utils.ensembl_rest_client import requests


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
