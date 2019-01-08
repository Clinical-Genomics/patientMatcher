# -*- coding: utf-8 -*-

import logging
from pymongo import MongoClient

LOG = logging.getLogger(__name__)

def delete_by_query(query, mongo_db, mongo_collection):
    """Deletes one or more entries matching a query from a database collection

    Args:
        query(dict): query to be used for deleting the entries
        mongo_db(pymongo.database.Database)
        mongo_collection(str): the name of a collection

    Returns:
        deleted_entries(int): the number of deleted deleted entries
    """

    LOG.info('Removing entries from collection "{0}" using the following parameters:{1}'.format(mongo_collection, query))
    deleted_entries = 0
    try:
        result = mongo_db[mongo_collection].delete_many(query)
        deleted_entries = result.deleted_count

    except Exception as err:
        LOG.fatal("An error occurred while performing delete: {}".format(err))
        sys.exit

    return deleted_entries
