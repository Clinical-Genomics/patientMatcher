# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

def create_app():
    #configuration files are relative to the instance folder
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    if not app.config.get('DB_URI') or not app.config.get('DB_NAME'):
        LOG.error('Please use values for DB_URI and DB_NAME parameters in config file.')
        return None

    if not app.config.get('MAX_GT_SCORE') or not app.config.get('MAX_PHENO_SCORE') or not (app.config.get('MAX_PHENO_SCORE') + app.config.get('MAX_GT_SCORE')) == 1:
        LOG.error('Please chech that MAX_GT_SCORE and MAX_PHENO_SCORE have valid values')
        return None

    if not app.config.get('MAX_RESULTS') or not isinstance(app.config.get('MAX_RESULTS'), int):
        LOG.error('MAX_RESULTS parameter in config file must be a number')
        return None

    client = MongoClient(app.config['DB_URI'])
    app.db = client[app.config['DB_NAME']]
    app.register_blueprint(server.views.blueprint)
    return app


def run_app():
    app = create_app()
    if app:
        host = app.config.get('HOST', '127.0.0.1')
        port = app.config.get('PORT', '9020')
        app.run(port=port, host=host)
    else:
        LOG.error('Fix config issues before running the app')


if __name__ == '__main__':
    create_app()


import patientMatcher.server.views
