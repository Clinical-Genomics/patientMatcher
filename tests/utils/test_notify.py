# -*- coding: utf-8 -*-
import pymongo
from patientMatcher.utils.notify import notify_match_external, notify_match_internal

def test_notify_match_external(match_obs, mock_sender, mock_mail):

    match_obj = match_obs[0] #an external match object with results

    # When calling the function that sends external match notifications
    notify_match_external(match_obj, mock_sender, mock_mail)

    # make sure send method was called
    assert mock_mail._send_was_called

    # and that mail object message was set correctly
    assert mock_mail._message


def test_notify_match_internal(database, match_obs, mock_sender, mock_mail):

    match_obj = match_obs[2] # an internal match object with results

    # insert patient used as query in database:
    assert database['patients'].find().count() == 0
    database['patients'].insert_one({ '_id' : 'external_patient_1'})
    assert database['patients'].find().count() == 1

    # When calling the function that sends internal match notifications
    notify_match_internal(database, match_obj, mock_sender, mock_mail)

    # make sure send method was called
    assert mock_mail._send_was_called

    # and that mail object message was set correctly
    assert mock_mail._message
