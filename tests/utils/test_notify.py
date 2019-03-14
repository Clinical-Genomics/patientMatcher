# -*- coding: utf-8 -*-
import pymongo
from patientMatcher.utils.notify import notify_match_external, notify_match_internal, html_format

def test_notify_match_external(match_objs, mock_sender, mock_mail):

    match_obj = match_objs[0] #an external match object with results
    assert match_obj['match_type'] == 'external'

    # When calling the function that sends external match notifications
    notify_complete = True # test notification of complete patient data by email
    notify_match_external(match_obj, mock_sender, mock_mail, notify_complete)

    # make sure send method was called
    assert mock_mail._send_was_called

    # and that mail object message was set correctly
    assert mock_mail._message


def test_notify_match_internal(database, match_objs, mock_sender, mock_mail):

    match_obj = match_objs[2] # an internal match object with results
    assert match_obj['match_type'] == 'internal'

    # insert patient used as query in database:
    assert database['patients'].find().count() == 0
    database['patients'].insert_one({ '_id' : 'external_patient_1'})
    assert database['patients'].find().count() == 1

    # When calling the function that sends internal match notifications
    notify_complete = False # test notification of partial patient data by email
    notify_match_internal(database, match_obj, mock_sender, mock_mail, notify_complete)

    # Test the function that formats the matching results to HTML:
    formatted_results = html_format(match_obj['results'])
    assert '<div style="margin-left: 0em">' in formatted_results

    # make sure send method was called
    assert mock_mail._send_was_called

    # and that mail object message was set correctly
    assert mock_mail._message
