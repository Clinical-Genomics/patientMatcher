# -*- coding: utf-8 -*-
import os

from patientMatcher.resources import path_to_hpo_terms
from patientMatcher.server import configure_email_error_logging, create_app
from patientMatcher.server.__init__ import available_phenotype_resources
from patientMatcher.utils.notify import TlsSMTPHandler


def test_create_app():
    """Tests the function that creates the app"""

    assert create_app()


def test_available_phenotype_resources():
    """Test function response when resource files (HPO terms and phenotype annotations) are both present"""
    assert available_phenotype_resources()


def test_available_phenotype_resources_missing_resource():
    """Test function response when one resource file is missing"""

    # GIVEN one of the required files missing (here it's been renamed)
    temp_file = ".".join([path_to_hpo_terms, "temp"])
    os.rename(path_to_hpo_terms, temp_file)

    # The function should return False
    assert available_phenotype_resources() is False

    # Revert original resource name
    os.rename(temp_file, path_to_hpo_terms)


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
