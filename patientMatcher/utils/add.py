# -*- coding: utf-8 -*-

import sys
import enlighten
import json
import logging
from pymongo import MongoClient

from patientMatcher.parse.patient import mme_patient
from patientMatcher.match.handler import external_matcher

LOG = logging.getLogger(__name__)

def load_demo(path_to_json_data, mongo_db, host):
    """Inserts demo patient data into database
        Demo data consists of a set of 50 patients from this paper: http://onlinelibrary.wiley.com/doi/10.1002/humu.22850

        Args:
            path_to_demo_data(str): absolute path to json file containing the demo patients.
            mongo_db(pymongo.database.Database)
            host(str): MME_HOST parameter in config file

        Returns:
            inserted_ids(list): the database ID of the inserted patients
    """
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

                inserted_id = backend_add_patient(mongo_db=mongo_db, host=host, patient=patient)[1]
                if inserted_id:
                    inserted_ids.append(inserted_id)
                pbar.update()

    except Exception as err:
        LOG.fatal("An error occurred while importing benchmarking patients: {}".format(err))

    return inserted_ids


def backend_add_patient(mongo_db, host, patient, match_external=False):
    """
        Insert or update a patient in patientMatcher database

        Args:
            mongo_db(pymongo.database.Database)
            host(str): MME_HOST parameter in config file
            patient(dict) : a MME patient entity

        Returns:
            inserted_id(str) : the ID of the inserted patient or None if patient couldn't be saved
    """
    modified = None
    upserted = None
    matching_obj = None

    try:
        result = mongo_db['patients'].replace_one({'_id': patient['_id']}, patient , upsert=True)
        modified = result.modified_count
        upserted = result.upserted_id

    except Exception as err:
        LOG.fatal("Error while inserting a patient into database: {}".format(err))

    # this will happen only if patient is added via POST request,
    # and if there is a change in patients' collections (new patient or updated patient)
    # Matching is not triggered by inserting demo data into database
    if match_external and (modified or upserted):
        matching_obj = external_matcher(mongo_db, host, patient)
        #save matching object to database
        mongo_db['matches'].insert_one(matching_obj)

    return modified, upserted, matching_obj


def add_node(mongo_db, obj, is_client):
    """
        Insert a new node (client or server) into the database

        Args:
            mongo_db(pymongo.database.Database)
            obj(dict): a client or a server object to add to database
            is_client(bool): if True the new node a client of this server, if False this server is a client of the new the node

        Returns:
            inserted_id(str), collection(str): a tuple with values inserted_id and collection name
    """
    inserted_id = None
    collection = None

    if is_client:
        collection = "clients"
    else:
        collection = "nodes"

    try:
        inserted_id = mongo_db[collection].insert_one(obj).inserted_id
    except Exception as err:
        LOG.fatal('Error while inserting a new client/server node to database:{}'.format(err))

    return inserted_id, collection
