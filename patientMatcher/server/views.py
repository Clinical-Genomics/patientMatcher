# -*- coding: utf-8 -*-

import logging
from flask import Blueprint, request, current_app, jsonify
from patientMatcher import create_app
from patientMatcher.utils.add import backend_add_patient
from patientMatcher.auth.auth import authorize
from patientMatcher.parse.patient import validate_api, mme_patient
from patientMatcher.constants import STATUS_CODES
from . import controllers

LOG = logging.getLogger(__name__)
blueprint = Blueprint('server', __name__)

@blueprint.route('/patient/add', methods=['POST'])
def add():
    """Add patient to database"""
    #check if request is authorized
    if not authorize(current_app.db, request):
        return controllers.bad_request(401)

    try: # make sure request has valid json data
        request_json = request.get_json(force=True)
    except Exception as err:
        LOG.info("Json data in request is not valid:{}".format(err))
        return controllers.bad_request(400)

    try: # validate json data against MME API
        validate_api(json_obj=request_json, is_request=True)
    except Exception as err:
        LOG.info("Patient data does not conform to API:{}".format(err))
        return controllers.bad_request(422)

    formatted_patient = mme_patient(json_patient=request_json['patient'], compute_phenotypes=True)
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


@blueprint.route('/patient/delete/<patient_id>', methods=['DELETE'])
def delete(patient_id):
    #check if request is authorized
    resp = None
    if not authorize(current_app.db, request): # not authorized, return a 401 status code
        message = STATUS_CODES[401]['message']
        resp = jsonify(message)
        resp.status_code = 401

    LOG.info('Authorized client is removing patient with id {}'.format(patient_id))
    message = controllers.delete_patient(current_app.db, patient_id)
    resp = jsonify(message)
    resp.status_code = 200
    return resp


@blueprint.route('/patient/view', methods=['GET'])
def view():
    #check if request is authorized
    resp = None
    if authorize(current_app.db, request):
        LOG.info('Authorized client requests all patients..')
        results = controllers.get_patients(database=current_app.db)
        resp = jsonify(results)
        resp.status_code = 200

    else: # not authorized, return a 401 status code
        message = STATUS_CODES[401]['message']
        resp = jsonify(message)
        resp.status_code = 401

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
