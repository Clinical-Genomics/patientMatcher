# -*- coding: utf-8 -*-
import logging
from patientMatcher.utils.patient import patients
from patientMatcher.parse.patient import json_patients

LOG = logging.getLogger(__name__)

def get_patients(database, patient_ids=None):
    """return all patients in response to client"""
    mme_patients = list(patients(database))
    json_like_patients = json_patients(mme_patients)

    return json_like_patients
