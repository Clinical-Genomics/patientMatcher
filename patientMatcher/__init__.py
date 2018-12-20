# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)

#configuration files are relative to the instance folder
app = Flask(__name__, template_folder='server/templates', instance_relative_config=True)
app.config.from_pyfile('config.py')
