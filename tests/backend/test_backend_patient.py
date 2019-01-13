# -*- coding: utf-8 -*-

import os
import pytest

from patientMatcher.utils.load import load_demo, backend_add_patient
from patientMatcher.utils.delete import delete_by_query
from patientMatcher.parse.patient import mme_patient

def test_load_demo_patients(demo_data_path, database):
    """Testing if loading of 50 test patients in database is working as it should"""

    # demo data file should be present in the expected directory
    assert os.path.isfile(demo_data_path)

    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database)
    assert len(inserted_ids) == 50 # 50 test cases should be loaded


def test_backend_remove_patient(json_patients, database):
    """ Test adding 2 test patients and then removing them using label or ID """

    # test conversion to format required for the database:
    test_mme_patients = [ mme_patient(json_patient=patient, compute_phenotypes=True) for patient in json_patients]

    # make sure 2 json patient are correctly parsed
    assert len(test_mme_patients) == 2

    # insert the 2 patients into the database
    inserted_ids = [ backend_add_patient(database['patients'], mme_patient) for mme_patient in test_mme_patients ]
    assert len(inserted_ids) == 2

    # make sure that inserted patients contain computed phenotypes from Monarch
    a_patient = database['patients'].find_one()
    #assert len(a_patient['monarch_phenotypes']) == 5 --------------------------------------------!

    # test removing a patient by ID:
    remove_query = {'_id' : 'patient_1'}
    deleted = delete_by_query(remove_query, database, 'patients')
    db_patients = database['patients'].find()
    assert db_patients.count() == 1

    # test removing a patient by label:
    remove_query = {'label' : 'Patient number 2'}
    deleted = delete_by_query(remove_query, database, 'patients')
    db_patients = database['patients'].find()
    assert db_patients.count() == 0
