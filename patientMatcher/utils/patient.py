# -*- coding: utf-8 -*-

import logging

LOG = logging.getLogger(__name__)

def patients(database, ids=None):
    """Get all patients in the database

    Args:
        database(pymongo.database.Database)
        ids(list): a list of IDs to return only specified patients

    Returns:
        results(Iterable[dict]): list of patients from mongodb patients collection
    """
    results = None
    query = {}
    if ids: # if only specified patients should be returned
        LOG.info('Querying patients for IDs {}'.format(ids))
        query['_id'] = {'$in' : ids}

    else:
        LOG.info('Return all patients in database')

    results = database['patients'].find(query)
    return results
