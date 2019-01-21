# -*- coding: utf-8 -*-
import logging
from flask import jsonify
from patientMatcher.constants import STATUS_CODES
from patientMatcher.utils.patient import patients
from patientMatcher.utils.delete import delete_by_query
from patientMatcher.parse.patient import json_patients

LOG = logging.getLogger(__name__)

def get_patients(database, patient_ids=None):
    """return all patients in response to client"""
    mme_patients = list(patients(database, patient_ids))
    json_like_patients = json_patients(mme_patients)

    return json_like_patients


def bad_request(error_code):
    """Crete an automatic response based on custom error codes"""
    message = STATUS_CODES[error_code]['message']
    resp = jsonify(message)
    resp.status_code = error_code
    return resp


def delete_patient(database, patient_id):
    """Remove a patient by ID"""
    message = ''
    query = {'_id' : patient_id}
    deleted = delete_by_query(query, database, 'patients')
    if deleted == 1:
        message = 'Patient was successfully deleted from database'
    else:
        message = 'ERROR. Could not delete a patient with ID {} from database'.format(patient_id)
    return message
