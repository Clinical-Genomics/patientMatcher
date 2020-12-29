# -*- coding: utf-8 -*-
import coloredlogs
import os
from pymongo import MongoClient
import logging
from flask import Flask
from flask_mail import Mail
from . import views

LOG = logging.getLogger(__name__)


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

    app.register_blueprint(views.blueprint)
    return app
