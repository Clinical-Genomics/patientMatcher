# -*- coding: utf-8 -*-

import logging
from flask import Blueprint, request, current_app, jsonify
from patientMatcher import create_app
from patientMatcher.utils.add import backend_add_patient
from patientMatcher.auth.auth import authorize
from patientMatcher.match.handler import internal_matcher

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
    modified, inserted = backend_add_patient(mongo_db=current_app.db, patient=formatted_patient, match_external=True)
    message = ''

    if modified:
        message = 'Patient was successfully updated.'
    elif inserted:
        message = 'Patient was successfully inserted into database.'
    else:
        message = 'Database content is unchanged.'

    resp = jsonify(message)
    resp.status_code = 200
    return resp


@blueprint.route('/patient/delete/<patient_id>', methods=['DELETE'])
def delete(patient_id):
    #check if request is authorized
    resp = None
    if not authorize(current_app.db, request): # not authorized, return a 401 status code
        message = STATUS_CODES[401]['message']
        resp = jsonify(message)
        resp.status_code = 401
        return resp

    LOG.info('Authorized client is removing patient with id {}'.format(patient_id))
    message = controllers.delete_patient(current_app.db, patient_id)
    resp = jsonify(message)
    resp.status_code = 200
    return resp


@blueprint.route('/patient/view', methods=['GET'])
def view():
    """Get all patients in database"""
    resp = None
    if authorize(current_app.db, request):
        LOG.info('Authorized client requests all patients..')
        results = controllers.get_patients(database=current_app.db)
        resp = jsonify(results)
        resp.status_code = 200

    else: # not authorized, return a 401 status code
        return controllers.bad_request(401)

    return resp


@blueprint.route('/patient/matches', methods=['GET'])
def matches():
    return "Get all matches for a patient ID"


@blueprint.route('/match/external/<patient_id>', methods=['POST'])
def match_external(patient_id):
    """Trigger a patient matching on external nodes by providing a patient ID"""
    resp = None
    if not authorize(current_app.db, request): # not authorized, return a 401 status code
        message = STATUS_CODES[401]['message']
        resp = jsonify(message)
        resp.status_code = 401
        return resp

    LOG.info('Authorized clients is matching patient with ID {} against external nodes'.format(patient_id))
    query_patient = controllers.patient(current_app.db, patient_id)

    if not query_patient:
        LOG.error('ERROR. Could not find amy patient with ID {} in database'.format(patient_id))
        message = "ERROR. Could not find amy patient with ID {} in database".format(patient_id)
        resp = jsonify(message)
        resp.status_code = 200
        return resp

    results, errors = controllers.match_external(current_app.db, query_patient)
    resp = jsonify(results)
    resp.status_code = 200
    return resp


@blueprint.route('/match', methods=['POST'])
def match_internal():
    """Match a query patient against patients from local database and
    return a response containing patients which are most similar to the
    query patient"""

    query_patient = controllers.check_request(current_app.db, request)
    if isinstance(query_patient, int): # some error must have occurred during validation
        return controllers.bad_request(query_patient)

    LOG.info('Matching a query patient against database')

    max_pheno_score = current_app.config.get('MAX_PHENO_SCORE', 0.5) # get max pheno score from app settings, if available
    max_geno_score = current_app.config.get('MAX_GT_SCORE', 0.5) # get max genotyping score from app settings, if available

    # get a list of matching patients ordered by score
    matches = internal_matcher(current_app.db, query_patient, max_pheno_score, max_geno_score)

    validate_response = controllers.validate_response({'results': matches})
    if isinstance(validate_response, int): # some error must have occurred during validation
        return controllers.bad_request(validate_response)

    LOG.info('Found {} matching patients in database'.format(len(matches)))

    # return response with results
    resp = jsonify(validate_response)
    resp.status_code = 200
    return resp
