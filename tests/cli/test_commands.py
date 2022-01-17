#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask_mail import Message
from patientMatcher.cli.commands import cli


def test_appname(mock_app):
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, ["test", "name"])
    assert result.output == "patientMatcher\n"


def test_help(mock_app):
    """Test invoking the cli with --help argument"""
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, ["add", "client", "--help"])
    assert result.exit_code == 0


def test_run_no_args(mock_app):
    """Test invoking the cli without arguments"""
    runner = mock_app.test_cli_runner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0


def test_sendemail(mock_app, mock_mail):
    mock_app.mail = mock_mail
    mock_app.config["MAIL_USERNAME"] = "sender@email.com"

    runner = mock_app.test_cli_runner()
    # When invoking the test email command with a recipient paramrter
    result = runner.invoke(cli, ["test", "email", "--recipient", "test_user@mail.com"])

    # Make sure that mock mail send method was called and mock email is sent
    assert mock_mail._send_was_called
    assert mock_mail._message
