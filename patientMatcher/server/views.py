# -*- coding: utf-8 -*-

import logging
from flask import Blueprint, request, current_app, jsonify
from patientMatcher import create_app
from patientMatcher.utils.add import backend_add_patient
from patientMatcher.auth.auth import authorize
from patientMatcher.match.handler import database_matcher

from patientMatcher.parse.patient import validate_api, mme_patient
from patientMatcher.constants import STATUS_CODES
from . import controllers

LOG = logging.getLogger(__name__)
blueprint = Blueprint('server', __name__)

@blueprint.route('/patient/add', methods=['POST'])
def add():
    """Add patient to database"""

    formatted_patient = controllers.check_request(current_app.db, request)
    if isinstance(formatted_patient, int): # some error must have occurred during validation
        return controllers.bad_request(formatted_patient)

    # else import patient to database
    modified, inserted = backend_add_patient(current_app.db['patients'], formatted_patient)
    message = ''

    if modified:
        message = 'Patient was successfully updated.'.format(formatted_patient['_id'])
    elif inserted:
        message = 'Patient was successfully inserted into database.'.format(formatted_patient['_id'])
    else:
        message = 'Database content is unchanged.'

    resp = jsonify(message)
    resp.status_code = 200
    return resp


@blueprint.route('/patient/delete', methods=['DELETE'])
def delete():
    return "Patient delete"


@blueprint.route('/patient/view', methods=['GET'])
def view():
    """Get all patients in database"""
    resp = None
    if authorize(current_app.db, request):
        LOG.info('Authorized clients requests all patients..')
        results = controllers.get_patients(database=current_app.db)
        resp = jsonify(results)
        resp.status_code = 200

    else: # not authorized, return a 401 status code
        return controllers.bad_request(401)

    return resp


@blueprint.route('/patient/matches', methods=['GET'])
def matches():
    return "Get all matches for a patient ID"


@blueprint.route('/match/external', methods=['POST'])
def match_external():
    return "Match patient against external nodes"


@blueprint.route('/match', methods=['POST'])
def match_internal():
    """Match a query patient against patients from local database and
    return a response with the patients which are most similar to the
    query patient"""

    query_patient = controllers.check_request(current_app.db, request)
    if isinstance(query_patient, int): # some error must have occurred during validation
        return controllers.bad_request(query_patient)

    LOG.info('Matching a query patient against database')

    max_pheno_score = current_app.config.get('MAX_PHENO_SCORE', 0.5) # get max pheno score from app settings, if available
    max_geno_score = current_app.config.get('MAX_GT_SCORE', 0.5) # get max genotyping score from app settings, if available

    # get a list of matching patients ordered by score
    matches = database_matcher(current_app.db, query_patient, max_pheno_score, max_geno_score)

    validate_response = controllers.validate_response({'results': matches})
    if isinstance(validate_response, int): # some error must have occurred during validation
        return controllers.bad_request(validate_response)

    LOG.info('Found {} matching patients in database'.format(len(matches)))

    # return response with results
    resp = jsonify(validate_response)
    resp.status_code = 200
    return resp
