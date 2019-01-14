# -*- coding: utf-8 -*-

import logging
from flask import Blueprint
from patientMatcher import create_app

LOG = logging.getLogger(__name__)
blueprint = Blueprint('server', __name__)

@blueprint.route('/patient/add')
def add():
    return "Patient add"


@blueprint.route('/patient/delete')
def delete():
    return "Patient delete"


@blueprint.route('/patient/view')
def view():
    return "Get all patients in db"


@blueprint.route('/patient/matches')
def matches():
    return "Get all matches for a patient ID"


@blueprint.route('/match/external')
def match_external():
    return "Match patient against external nodes"


@blueprint.route('/match/internal')
def match_internal():
    return "Match patient against patients within same node"
