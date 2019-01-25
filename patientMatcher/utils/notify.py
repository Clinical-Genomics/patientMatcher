# -*- coding: utf-8 -*-

import logging

LOG = logging.getLogger(__name__)

def notify_match(match_obj, admin_email, query_patient, external_match=False):
    """Send an email to patient contact to notify a match

    Args:
        match_obj(dict): an object containing both query patient(dict) and matching results(list)
        admin_email(str): email of sender
        query_patient(dict): patient object used for the query
        external_match(bool): True == match in connected nodes, False == match with other patients in database

    Returns:
        Boh!
    """

    if 


def email_body():
