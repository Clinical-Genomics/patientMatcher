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
        LOG.info('Configuring app from environment variable')
        app = Flask(__name__)
        app.config.from_envvar('PMATCHER_CONFIG')
    except:
        LOG.warning('Environment variable settings not found, configuring from instance file.')
        app_root=os.path.abspath(__file__).split('patientMatcher')[0]
        LOG.info('app root is: {}'.format(app_root))
        app = Flask(__name__, instance_path=os.path.join(app_root, 'patientMatcher', 'instance'), instance_relative_config=True)
        app.config.from_pyfile('config.py')

    client = MongoClient(app.config['DB_URI'])
    app.client = client
    app.db = client[app.config['DB_NAME']]

    if app.config.get('MAIL_SERVER'):
        mail = Mail(app)
        app.mail = mail

    app.register_blueprint(views.blueprint)
    return app
