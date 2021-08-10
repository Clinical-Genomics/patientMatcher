# -*- coding: utf-8 -*-

import os

import pytest
from patientMatcher.parse.patient import mme_patient
from patientMatcher.utils.add import backend_add_patient, load_demo_patients
from patientMatcher.utils.delete import delete_by_query


def test_load_demo_patients(demo_data_path, database):
    """Testing if loading of 50 test patients in database is working as it should"""

    # demo data file should be present in the expected directory
    assert os.path.isfile(demo_data_path)

    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo_patients(demo_data_path, database)
    assert len(inserted_ids) == 50  # 50 test cases should be loaded

    # make sure that trying to re-insert the same patients will not work
    re_inserted_ids = load_demo_patients(demo_data_path, database)
    assert len(re_inserted_ids) == 0

    # try to call load_demo with an invalid patient file:
    inserted_ids = load_demo_patients("this_is_a_fakey_json_file.json", database)
    assert len(inserted_ids) == 0


def test_backend_remove_patient(gpx4_patients, database):
    """ Test adding 2 test patients and then removing them using label or ID """

    # test conversion to format required for the database:
    test_mme_patients = [mme_patient(json_patient=patient) for patient in gpx4_patients]

    # make sure 2 json patient are correctly parsed
    assert len(test_mme_patients) == 2

    # insert the 2 patients into the database
    inserted_ids = [
        backend_add_patient(mongo_db=database, patient=mme_patient, match_external=False)
        for mme_patient in test_mme_patients
    ]
    assert len(inserted_ids) == 2

    # make sure that inserted patients contain computed phenotypes from Monarch
    a_patient = database["patients"].find_one()
    assert a_patient

    # test removing a patient by ID:
    remove_query = {"_id": "P0001058"}
    deleted = delete_by_query(remove_query, database, "patients")
    db_patients = database["patients"].find()
    assert len(list(db_patients)) == 1

    # test removing a patient by label:
    remove_query = {"label": "350_2-test"}
    deleted = delete_by_query(remove_query, database, "patients")
    assert database["patients"].find_one() is None
