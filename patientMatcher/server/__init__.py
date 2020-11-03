# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
import logging
from flask import Flask
from flask_mail import Mail
from . import views

logging.basicConfig(level=logging.INFO)
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

    db_username = app.config["DB_USERNAME"]
    db_password = app.config["DB_PASSWORD"]
    # If app is runned from inside a container, override host port
    db_host = os.getenv("MONGODB_HOST") or app.config["DB_HOST"]
    db_port = app.config["DB_PORT"]
    db_name = app.config["DB_NAME"]
    db_uri = f"mongodb://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

    client = MongoClient(db_uri)
    app.client = client
    app.db = client[app.config["DB_NAME"]]
    LOG.info("database connection info:{}".format(app.db))

    if app.config.get("MAIL_SERVER"):
        mail = Mail(app)
        app.mail = mail

    app.register_blueprint(views.blueprint)
    return app
