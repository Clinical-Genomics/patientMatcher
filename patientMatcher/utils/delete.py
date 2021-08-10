# -*- coding: utf-8 -*-

import logging

from pymongo import MongoClient

LOG = logging.getLogger(__name__)


def drop_all_collections(mongo_db):
    """Deletes all collections from the database. Most likely involked when a demo instance is created.

    Args:
        mongo_db(pymongo.database.Database)
    """
    LOG.warning(f"Dropping all existing collections in database")
    for collection in mongo_db.collection_names():
        mongo_db[collection].drop()


def delete_by_query(query, mongo_db, mongo_collection):
    """Deletes one or more entries matching a query from a database collection

    Args:
        query(dict): query to be used for deleting the entries
        mongo_db(pymongo.database.Database)
        mongo_collection(str): the name of a collection

    Returns:
        deleted_entries(int): the number of deleted deleted entries or the error
    """

    LOG.info(
        'Removing entries from collection "{0}" using the following parameters:{1}'.format(
            mongo_collection, query
        )
    )
    deleted_entries = 0

    try:
        result = mongo_db[mongo_collection].delete_many(query)
        deleted_entries = result.deleted_count
    except Exception as err:
        deleted_entries = err

    return deleted_entries
