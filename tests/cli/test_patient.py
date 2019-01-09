# -*- coding: utf-8 -*-

import os
import pytest

from patientMatcher.utils.load import load_demo

def test_load_demo_patients(demo_data_path, database):
    """Testing if loading of 50 test patients in database is working as it should"""

    # demo data file should be present in the expected directory
    assert os.path.isfile(demo_data_path)

    # load demo data to mock database using function located under utils/load
    inserted_ids = load_demo(demo_data_path, database)
    assert len(inserted_ids) == 50 # 50 test cases should be loaded

def test_backend_delete_patient()
