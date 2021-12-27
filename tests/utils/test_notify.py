# -*- coding: utf-8 -*-
from patientMatcher.__version__ import __version__
from patientMatcher.utils.notify import (
    admins_email_format,
    html_format,
    notify_match_external,
    notify_match_internal,
)


def test_admins_email_format():
    unformatted_admins = '["foo@mail.com", "bar@mail.com"]'
    formatted_admins = admins_email_format(unformatted_admins)
    assert isinstance(formatted_admins, list)


def test_notify_match_external(mock_app, match_objs, mock_sender, mock_mail):

    match_obj = match_objs[0]  # an external match object with results
    assert match_obj["match_type"] == "external"

    with mock_app.app_context():

        # When calling the function that sends external match notifications
        notify_complete = True  # test notification of complete patient data by email
        notify_match_external(match_obj, mock_sender, mock_mail, notify_complete)

        # make sure send method was called
        assert mock_mail._send_was_called

        # and that mail object message was set correctly
        assert match_obj["data"]["patient"]["id"] in mock_mail._message.html
        assert __version__ in mock_mail._message.html


def test_notify_match_internal(database, match_objs, mock_sender, mock_mail):

    match_obj = match_objs[2]  # an internal match object with results
    assert match_obj["match_type"] == "internal"

    # insert patient used as query in database:
    assert database["patients"].find_one() is None
    assert database["patients"].insert_one({"_id": "external_patient_1"}).inserted_id

    # When calling the function that sends internal match notifications
    notify_complete = False  # test notification of partial patient data by email
    notify_match_internal(database, match_obj, mock_sender, mock_mail, notify_complete)

    # Test the function that formats the matching results to HTML:
    formatted_results = html_format(match_obj["results"])
    assert '<div style="margin-left: 0em">' in formatted_results

    # make sure send method was called
    assert mock_mail._send_was_called

    # and that mail object message was set correctly
    assert match_obj["data"]["patient"]["id"] in mock_mail._message.html
    assert __version__ in mock_mail._message.html
