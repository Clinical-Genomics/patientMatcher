# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

def create_app(info=None):
    #configuration files are relative to the instance folder
    app = Flask(__name__, template_folder='server/templates', instance_relative_config=True)

    pyfile = 'config.py'
    if info:
        pyfile = info

    app.config.from_pyfile(pyfile)

    client = MongoClient(app.config['DB_URI'])
    app.db = client[app.config['DB_NAME']]
    return app


if __name__ == '__main__':
    create_app()
