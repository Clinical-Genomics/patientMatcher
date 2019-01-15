# -*- coding: utf-8 -*-

import logging
from flask import Blueprint, request, current_app, jsonify
from patientMatcher import create_app
from patientMatcher.auth.auth import authorize
from patientMatcher.constants import STATUS_CODES
from . import controllers

LOG = logging.getLogger(__name__)
blueprint = Blueprint('server', __name__)

@blueprint.route('/patient/add', methods=['POST'])
def add():
    return "Patient add"


@blueprint.route('/patient/delete', methods=['DELETE'])
def delete():
    return "Patient delete"


@blueprint.route('/patient/view', methods=['GET'])
def view():
    #check if request is authorized
    resp = None
    if authorize(current_app.db, request):
        LOG.info('Authorized clients requests all patients..')
        results = controllers.get_patients(database=current_app.db)
        resp = jsonify(results)
        resp.status_code = STATUS_CODES['ok']['status_code']

    else: # not authorized, return a 401 status code
        message = STATUS_CODES['unauthorized']['message']
        resp = jsonify(message)
        resp.status_code = STATUS_CODES['unauthorized']['status_code']

    return resp


@blueprint.route('/patient/matches', methods=['GET'])
def matches():
    return "Get all matches for a patient ID"


@blueprint.route('/match', methods=['POST'])
def match_external():
    return "Match patient against external nodes"


@blueprint.route('/match/internal', methods=['POST'])
def match_internal():
    return "Match patient against patients within same node"
