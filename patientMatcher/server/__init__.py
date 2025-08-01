# -*- coding: utf-8 -*-
import logging
import os
import sys
from pathlib import Path

import coloredlogs
from flask import Flask
from flask_mail import Mail
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    OperationFailure,
    ServerSelectionTimeoutError,
)

from patientMatcher.resources import path_to_hpo_terms, path_to_phenotype_annotations
from patientMatcher.utils.notify import TlsSMTPHandler, admins_email_format
from patientMatcher.utils.update import update_resources

from . import extensions, views

LOG = logging.getLogger(__name__)


def available_phenotype_resources():
    """Check that necessary resources (HPO terms and phenotype annotations) were downloaded and available"""
    for item in [path_to_hpo_terms, path_to_phenotype_annotations]:
        if Path(item).is_file() is False:
            return False

    return True


def configure_email_error_logging(app):
    """Setup logging of error/exceptions to email."""
    LOG.debug(f"Configuring email error logging to notify server admins:{app.config['ADMINS']}")

    mail_handler = TlsSMTPHandler(
        mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
        fromaddr=app.config["MAIL_USERNAME"],
        toaddrs=app.config["ADMINS"],
        subject=f"{app.name} - {app.config['DB_NAME']} - log error",
        credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.addHandler(mail_handler)
    logging.getLogger("werkzeug").addHandler(mail_handler)


def create_app():
    app = None
    try:
        app = Flask(__name__)
        app.config.from_envvar("PMATCHER_CONFIG")
    except Exception:
        LOG.warning(
            "PMATCHER_CONFIG env variable not found, configuring from instance file + env vars."
        )
        app_root = os.path.abspath(__file__).split("patientMatcher")[0]

        # check if config file exists under ../instance:
        instance_path = os.path.join(app_root, "patientMatcher", "instance")
        if not os.path.isfile(os.path.join(instance_path, "config.py")):  # running app from tests
            instance_path = os.path.join(app_root, "patientMatcher", "patientMatcher", "instance")

        app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
        app.config.from_pyfile("config.py")

    if app.config.get("ADMINS"):
        app.config["ADMINS"] = admins_email_format(app.config["ADMINS"])

    current_log_level = LOG.getEffectiveLevel()
    coloredlogs.install(level="DEBUG" if app.debug else current_log_level)

    # 🔇 Suppress PyMongo debug logs
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("pymongo.topology").setLevel(logging.WARNING)
    logging.getLogger("pymongo.pool").setLevel(logging.WARNING)
    logging.getLogger("pymongo.server").setLevel(logging.WARNING)

    mongo_client = MongoClient(app.config["DB_URI"], serverSelectionTimeoutMS=30000)
    try:
        mongo_client.server_info()
    except (ServerSelectionTimeoutError, OperationFailure, ConnectionFailure) as err:
        LOG.warning(f"Database connection error:{err}")
        sys.exit()

    app.client = mongo_client
    db_name = app.config["DB_NAME"]
    app.db = mongo_client[db_name]
    LOG.info(f"Connecting to database '{db_name}' on {app.db}")

    if app.config.get("TESTING") in ["False", False]:
        update_resources(test=False)

    # If phenotype resources are missing display error and exit
    if available_phenotype_resources() is False:
        LOG.error(
            "Required files hp.obo.txt and phenotype.hpoa not found on the server. Please download them with the command 'pmatcher update resources'."
        )
        return

    extensions.hpo.init_app()
    extensions.diseases.init_app()
    extensions.hpoic.init_app(app, extensions.hpo, extensions.diseases)

    for terms in [extensions.hpo.hps, extensions.diseases.diseases]:
        if not terms:
            LOG.error("An error occurred while parsing resource files.")
            return

    if app.config.get("MAIL_SERVER"):
        app.config["MAIL_SUPPRESS_SEND"] = False
        app.config["MAIL_DEBUG"] = True

        mail = Mail(app)
        app.mail = mail

        # Configure email logging of errors
        if app.debug is True and app.config.get("ADMINS"):
            configure_email_error_logging(app)

    app.register_blueprint(views.blueprint)

    return app
