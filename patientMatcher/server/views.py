# -*- coding: utf-8 -*-

import logging
from bson import json_util
import json
from flask import Blueprint, request, current_app, jsonify
from flask_negotiate import consumes, produces

from patientMatcher import create_app
from patientMatcher.utils.add import backend_add_patient
from patientMatcher.utils.notify import notify_match_external, notify_match_internal
from patientMatcher.auth.auth import authorize
from patientMatcher.match.handler import internal_matcher, patient_matches
from patientMatcher.parse.patient import validate_api, mme_patient
from patientMatcher.constants import STATUS_CODES
from . import controllers

LOG = logging.getLogger(__name__)
blueprint = Blueprint('server', __name__)
API_MIME_TYPE = 'application/vnd.ga4gh.matchmaker.v1.0+json'

@blueprint.route('/patient/add', methods=['POST'])
@consumes(API_MIME_TYPE, 'application/json')
@produces('application/json')
def add():
    """Add patient to database"""

    formatted_patient = controllers.check_request(current_app.db, request)
    if isinstance(formatted_patient, int): # some error must have occurred during validation
        return controllers.bad_request(formatted_patient)

    # else import patient to database
    modified, inserted, matching_obj= backend_add_patient(mongo_db=current_app.db, patient=formatted_patient,
        match_external=True, host=current_app.config.get('MME_HOST'))
    message = {}

    if modified:
        message['message'] = 'Patient was successfully updated.'
    elif inserted:
        message['message'] = 'Patient was successfully inserted into database.'
    else:
        message['message'] = 'Database content is unchanged.'

    # if patient is matching any other patient on other nodes
    # and match notifications are on
    if current_app.config.get('MAIL_SERVER') and matching_obj and len(matching_obj.get('results')):
        # send an email to patient's contact:
        notify_match_external(match_obj=matching_obj, admin_email=current_app.config.get('MAIL_USERNAME'), mail=current_app.mail)

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


@blueprint.route('/metrics', methods=['GET'])
def metrics():
    """Get database metrics"""
    resp = None
    if authorize(current_app.db, request):
        LOG.info('Authorized client requests metrics..')
        results = controllers.metrics(database=current_app.db)
        resp = jsonify({'metrics' : results, 'disclaimer' : current_app.config.get('DISCLAIMER')})
        resp.status_code = 200

    else: # not authorized, return a 401 status code
        return controllers.bad_request(401)

    return resp


@blueprint.route('/nodes', methods=['GET'])
def nodes():
    """Get a list of all nodes connected to this MME server"""
    resp = None
    if not authorize(current_app.db, request):
        message = STATUS_CODES[401]['message']
        resp = jsonify(message)
        resp.status_code = 401
        return resp

    LOG.info('Authorized client requests list of connected nodes..')
    results = controllers.get_nodes(database=current_app.db)
    resp = jsonify(results)
    resp.status_code = 200
    return resp


@blueprint.route('/matches/<patient_id>', methods=['GET'])
def matches(patient_id):
    """Get all matches (external and internal) for a patient ID"""
    LOG.info('getting all matches for patient {}'.format(patient_id))
    resp = None
    message = {}
    if not authorize(current_app.db, request): # not authorized, return a 401 status code
        message = STATUS_CODES[401]['message']
        resp = jsonify(message)
        resp.status_code = 401
        return resp

    # return only matches with at least one result
    results = patient_matches(current_app.db, patient_id)
    if results:
        message = json.loads(json_util.dumps({'matches' : results}))
    else:
        message['message'] = "Could not find any matches in database for patient ID {}".format(patient_id)
    resp = jsonify(message)
    resp.status_code = 200
    return resp


@blueprint.route('/match/external/<patient_id>', methods=['POST'])
def match_external(patient_id):
    """Trigger a patient matching on external nodes by providing a patient ID"""
    resp = None
    message = {}
    if not authorize(current_app.db, request): # not authorized, return a 401 status code
        message['message'] = STATUS_CODES[401]['message']
        resp = jsonify(message)
        resp.status_code = 401
        return resp

    LOG.info('Authorized clients is matching patient with ID {} against external nodes'.format(patient_id))
    query_patient = controllers.patient(current_app.db, patient_id)

    if not query_patient:
        LOG.error('ERROR. Could not find any patient with ID {} in database'.format(patient_id))
        message['message'] = "ERROR. Could not find any patient with ID {} in database".format(patient_id)
        resp = jsonify(message)
        resp.status_code = 200
        return resp

    node = request.args.get('node')

    # if search should be performed on a specific node, make sure node is in database
    if node and not current_app.db['nodes'].find({'_id':node}).count():
        LOG.info('ERROR, theres no node with id "{}" in database'.format(request.args['node']))
        message['message'] = 'ERROR. Could not find any connected node with id {} in database'.format(request.args['node'])
        resp = jsonify(message)
        resp.status_code = 200
        return resp

    host = current_app.config.get('MME_HOST') # Introduce yourself in request
    matching_obj = controllers.match_external(current_app.db, host, query_patient, node)

    if not matching_obj:
        message['message'] = "Could not find any other node connected to this MatchMaker server"
        resp = jsonify(message)
        resp.status_code = 200
        return resp

    results = matching_obj.get('results')

    # if patient is matching any other patient on other nodes
    # and match notifications are on
    if current_app.config.get('MAIL_SERVER') and matching_obj and len(results):
        # send an email to patient's contact:
        notify_match_external(match_obj=matching_obj, admin_email=current_app.config.get('MAIL_USERNAME'), mail=current_app.mail)

    resp = jsonify({'results':results})
    resp.status_code = 200
    return resp


@blueprint.route('/match', methods=['POST'])
@consumes(API_MIME_TYPE)
@produces(API_MIME_TYPE, 'application/json')
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
    max_results = current_app.config.get('MAX_RESULTS')

    # get a list of matching patients ordered by score
    match_obj = internal_matcher(current_app.db, query_patient, max_pheno_score, max_geno_score, max_results)
    # save matching object to database
    current_app.db['matches'].insert_one(match_obj)
    matches = match_obj['results'][0]['patients'] #results[0] because there is just one node (internal match)

    # if notifications are on and there are matching results
    if current_app.config.get('MAIL_SERVER') and len(matches):
        notify_match_internal(database=current_app.db, match_obj=match_obj,
            admin_email=current_app.config.get('MAIL_USERNAME'), mail=current_app.mail)


    validate_response = controllers.validate_response({'results': matches})
    if isinstance(validate_response, int): # some error must have occurred during validation
        return controllers.bad_request(validate_response)

    LOG.info('Found {} matching patients in database'.format(len(matches)))

    # return response with results
    validate_response["disclaimer"] = current_app.config.get('DISCLAIMER')
    resp = jsonify(validate_response)
    resp.status_code = 200
    return resp
