# -*- coding: utf-8 -*-

from patientMatcher.utils.add import load_demo
from patientMatcher.utils.patient import patients
import pymongo

def test_patients(demo_data_path, database):
    """Tests the function that retrieves patient objects"""

    # load demo data in mock database
    inserted_ids = load_demo(demo_data_path, database, False)
    assert type(inserted_ids) == list
    assert len(inserted_ids) == 50 # 50 test cases are loaded

    # get all 50 patients available in database
    all_patients = list(patients(database=database))
    assert len(all_patients) == 50

    # test collecting just a few patients:
    selected_patients = list(patients(database=database, ids=inserted_ids[:3]))
    assert len(inserted_ids[:3]) == 3
    assert len(selected_patients) == 3
