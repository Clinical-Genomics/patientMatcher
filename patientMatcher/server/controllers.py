# -*- coding: utf-8 -*-
import logging
from flask import jsonify
from jsonschema import ValidationError
from patientMatcher.constants import STATUS_CODES
from patientMatcher.utils.patient import patients
from patientMatcher.parse.patient import json_patient, validate_api, mme_patient
from patientMatcher.auth.auth import authorize
from patientMatcher.utils.delete import delete_by_query
from patientMatcher.match.handler import external_matcher

LOG = logging.getLogger(__name__)

def get_patients(database, patient_ids=None):
    """return all patients in response to client"""
    mme_patients = list(patients(database, patient_ids))
    json_like_patients = [json_patient(mmep) for mmep in mme_patients]
    return json_like_patients


def patient(database, patient_id):
    """Return a mme-like patient from database by providing its ID"""
    query_patient = None
    query_result = list(patients(database, ids=[patient_id]))
    if query_result:
        query_patient = query_result[0]
    return query_patient


def match_external(database, query_patient):
    """Trigger an external patient matching for a given patient object"""
    # trigger the matching and save the matching id to variable
    matching_obj = external_matcher(database, query_patient)
    # save matching object to database
    database['matches'].insert_one(matching_obj)

    return matching_obj


def check_request(database, request):
    """Check if request is valid, if it is return MME formatted patient
       Otherwise return error code.
    """
    check_result = None

    # check that request is using a valid auth token
    if not authorize(database, request):
        LOG.info("Request is not authorized")
        return 401

    try: # make sure request has valid json data
        request_json = request.get_json(force=True)
    except Exception as err:
        LOG.info("Json data in request is not valid:{}".format(err))
        return 400

    try: # validate json data against MME API
        validate_api(json_obj=request_json, is_request=True)
    except Exception as err:
        LOG.info("Patient data does not conform to API:{}".format(err))
        return 422

    formatted_patient = mme_patient(json_patient=request_json['patient'], compute_phenotypes=True)
    return formatted_patient


def validate_response(matches):
    """Validates patient matching results before sending them away in a response"""

    try: # validate json data against MME API
        validate_api(json_obj=matches, is_request=False)
    except ValidationError as err:
        LOG.info("Patient data does not conform to API:{}".format(err))
        return 422
    return matches


def bad_request(error_code):
    """Crete an automatic response based on custom error codes"""
    message = STATUS_CODES[error_code]['message']
    resp = jsonify(message)
    resp.status_code = error_code
    return resp


def delete_patient(database, patient_id):
    """Remove a patient by ID"""
    message = ''

    # first delete all matches in database for this patient:
    query = {'data.patient.id' : patient_id}
    deleted = delete_by_query(query, database, 'matches')
    LOG.info('deleted {} matche/s triggered by this patient'.format(deleted))


    query = {'_id' : patient_id}
    deleted = delete_by_query(query, database, 'patients')
    if deleted == 1:
        message = 'Patient and its matches were successfully deleted from database'
    else:
        message = 'ERROR. Could not delete a patient with ID {} from database'.format(patient_id)
    return message
