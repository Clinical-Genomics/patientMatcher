# -*- coding: utf-8 -*-
import os

from patientMatcher.resources import path_to_hpo_terms
from patientMatcher.server import configure_email_error_logging, create_app
from patientMatcher.server.__init__ import available_phenotype_resources
from patientMatcher.utils.notify import TlsSMTPHandler


def test_env_vars_parsing(monkeypatch):
    """Test that the env vars are correctly parsed when creating the app"""
    # GIVEN some params provided as env vars
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("TESTING", "False")
    monkeypatch.setenv("DB_PORT", "27017")
    monkeypatch.setenv("MAX_GT_SCORE", "0.7")
    monkeypatch.setenv("MAX_PHENO_SCORE", "0.3")
    monkeypatch.setenv("MAX_RESULTS", "3")
    monkeypatch.setenv("SCORE_THRESHOLD", "0.5")
    monkeypatch.setenv("MAIL_PORT", "586")
    monkeypatch.setenv("NOTIFY_COMPLETE", "False")

    app = create_app()

    # THEN the app should be created with the expected config values
    app.config["DEBUG"] is True
    app.config["TESTING"] is False
    app.config["DB_PORT"] == 27017
    app.config["MAX_GT_SCORE"] == 0.7
    app.config["MAX_PHENO_SCORE"] == 0.3
    app.config["MAX_RESULTS"] == 3
    app.config["SCORE_THRESHOLD"] == 0.5
    app.config["MAIL_PORT"] == 586
    app.config["NOTIFY_COMPLETE"] is False


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


def test_error_log_email(monkeypatch):
    """Test the app error logging via email"""

    # GIVEN an app with an ADMIN and configured email error logging params
    monkeypatch.setenv("ADMINS", '["app_admin_email"]')
    monkeypatch.setenv("MAIL_SERVER", "smtp.gmail.com")
    monkeypatch.setenv("MAIL_PORT", "587")
    monkeypatch.setenv("MAIL_USERNAME", "server_email")
    monkeypatch.setenv("MAIL_PASSWORD", "server_pw")
    monkeypatch.setenv("MAIL_USE_TLS", "True")

    app = create_app()

    configure_email_error_logging(app)

    # Then a TlsSMTPHandler should be among the app loggers
    handler = app.logger.handlers[0]
    assert isinstance(handler, TlsSMTPHandler)

    # And should contain the given settings
    assert handler.mailhost == "smtp.gmail.com"
    assert handler.mailport == 587
    assert handler.fromaddr == "server_email"
    assert handler.password == "server_pw"
    assert app.config["ADMINS"] == ["app_admin_email"]
    assert isinstance(handler.toaddrs, list)
