# -*- coding: utf-8 -*-

import sys
import enlighten
import json
import logging
from pymongo import MongoClient

from patientMatcher.parse.patient import mme_patient

LOG = logging.getLogger(__name__)

def load_demo(path_to_json_data, mongo_db):
    """Inserts demo patient data into database
        Demo data consists of a set of 50 patients from this paper:Benchmarking patients from paper: http://onlinelibrary.wiley.com/doi/10.1002/humu.22850

        Args:
            path_to_demo_data(str): absolute path to json file containing the demo patients.
            mongo_db(pymongo.database.Database)

        Returns:
            inserted_ids(list): the database ID of the inserted patients
    """

    patients_collection = mongo_db.patients
    patients = [] # a list of dictionaries
    inserted_ids = []

    #open json file and try to insert one patient at the time
    try:
        LOG.info('reading patients file')
        with open(path_to_json_data) as json_data:
            patients = json.load(json_data)
            # create a progress bar
            pbar = enlighten.Counter(total=len(patients), desc='', unit='patients')
            for json_patient in patients:

                #parse patient into format accepted by database
                patient = mme_patient(json_patient)

                inserted_id = backend_add_patient(patients_collection, patient)
                if inserted_id:
                    inserted_ids.append(inserted_id)
                pbar.update()

    except Exception as err:
        LOG.fatal("An error occurred while importing benchmarking patients: {}".format(err))
        sys.exit()

    return inserted_ids


def backend_add_patient(patients_collection, patient):
    """
        Insert a patient into matchbox database

        Args:
            patients_collection(pymongo.collection.Collection): a pymongo collection
            patient(dict) : a matchbox patient entity (org.broadinstitute.macarthurlab.matchbox.entities.Patient)

        Returns:
            result.inserted_id(str) : the ID of the inserted patient or None if patient couldn't be saved
    """

    LOG.info("Adding patient with ID {} to database".format(patient.get('_id')))
    inserted_id = None
    try:
        inserted_id = patients_collection.insert_one(patient).inserted_id
    except Exception as err:
        LOG.fatal("Error while inserting a patient into db: {}".format(err))

    return inserted_id
