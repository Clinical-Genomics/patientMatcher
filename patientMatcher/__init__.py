# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

def create_app():
    #configuration files are relative to the instance folder
    app = Flask(__name__, template_folder='server/templates', instance_relative_config=True)
    app.config.from_pyfile('config.py')

    client = MongoClient(app.config['DB_URI'])
    app.db = client[app.config['DB_NAME']]
    return app


def run_app():
    app = create_app()
    host = app.config.get('HOST', '127.0.0.1')
    port = app.config.get('PORT', '9020')
    app.run(port=port, host=host)


if __name__ == '__main__':
    create_app()
