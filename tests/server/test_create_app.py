# -*- coding: utf-8 -*-
from patientMatcher.server import configure_email_error_logging
from smtplib import SMTP
from patientMatcher.utils.notify import TlsSMTPHandler


def test_create_app(mock_app):
    """Tests the function that creates the app"""

    assert mock_app.client
    assert mock_app.db


def test_error_log_email(mock_app):
    """Test the app error logging via email"""

    # GIVEN an app with an ADMIN and configured email error logging params
    mail_host = "smtp.gmail.com"
    mail_port = 587
    server_email = "server_email"
    server_pw = "server_pw"

    mock_app.config["ADMINS"] = ["app_admin_email"]
    mock_app.config["MAIL_SERVER"] = mail_host
    mock_app.config["MAIL_PORT"] = mail_port
    mock_app.config["MAIL_USERNAME"] = server_email
    mock_app.config["MAIL_PASSWORD"] = server_pw

    configure_email_error_logging(mock_app)

    # Then a TlsSMTPHandler should be among the app loggers
    handler = mock_app.logger.handlers[0]
    assert isinstance(handler, TlsSMTPHandler)
    # And should contain the given settings
    assert handler.mailhost == mail_host
    assert handler.mailport == mail_port
    assert handler.fromaddr == server_email
    assert handler.password == server_pw
    assert handler.toaddrs == mock_app.config["ADMINS"]
    # assert handler.level
