# -*- coding: utf-8 -*-

import logging

import pymongo
from flask import request

LOG = logging.getLogger(__name__)

def authorize(database, request):
    """Validate request's token against database client collection

    Args:
        database(pymongo.database.Database)
        request(request): a request object

    Returns:
        authorized(bool): True or False
    """

    token = request.headers.get('X-Auth-Token')
    query = {'auth_token' : token}
    authorized = database['clients'].find(query).count()
    LOG.info('AUTH:{}'.format(bool(authorized)))
    return authorized
