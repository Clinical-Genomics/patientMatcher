# -*- coding: utf-8 -*-
import coloredlogs
import os
from pymongo import MongoClient
import logging
from flask import Flask
from flask_mail import Mail
from . import views
from patientMatcher.utils.notify import TlsSMTPHandler

LOG = logging.getLogger(__name__)


def configure_email_error_logging(app):
    """Setup logging of error/exceptions to email."""

    mail_handler = TlsSMTPHandler(
        mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
        fromaddr=app.config["MAIL_USERNAME"],
        toaddrs=app.config["ADMINS"],
        subject=f"{app.name} log error",
        credentials=(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"]),
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.addHandler(mail_handler)
    app.logger.exception(Exception("hello"))


def create_app():
    app = None
    try:
        LOG.info("Configuring app from environment variable")
        app = Flask(__name__)
        app.config.from_envvar("PMATCHER_CONFIG")
    except:
        LOG.warning("Environment variable settings not found, configuring from instance file.")
        app_root = os.path.abspath(__file__).split("patientMatcher")[0]

        # check if config file exists under ../instance:
        instance_path = os.path.join(app_root, "patientMatcher", "instance")
        if not os.path.isfile(os.path.join(instance_path, "config.py")):  # running app from tests
            instance_path = os.path.join(app_root, "patientMatcher", "patientMatcher", "instance")

        app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
        app.config.from_pyfile("config.py")

    current_log_level = LOG.getEffectiveLevel()
    coloredlogs.install(level="DEBUG" if app.debug else current_log_level)

    client = MongoClient(app.config["DB_URI"])
    app.client = client
    app.db = client[app.config["DB_NAME"]]
    LOG.info("database connection info:{}".format(app.db))

    if app.config.get("MAIL_SERVER"):
        mail = Mail(app)
        app.mail = mail

        # Configure email logging of errors
        if app.debug and app.config.get("ADMINS"):
            configure_email_error_logging(app)

    app.register_blueprint(views.blueprint)
    return app
