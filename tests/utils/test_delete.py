from patientMatcher.utils.add import load_demo_patients
from patientMatcher.utils.delete import drop_all_collections


def test_drop_all_collections(demo_data_path, database):
    """Test the functions that drop all existent collections from database before populating demo database"""
    # GIVEN a populated database
    load_demo_patients(demo_data_path, database)
    collections = database.collection_names()
    assert collections

    # WHEN drop_all_collections is invoked
    drop_all_collections(database)
    collections = database.collection_names()
    # THEN no collections should be found in database
    assert collections == []
