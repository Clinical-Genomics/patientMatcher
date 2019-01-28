# -*- coding: utf-8 -*-

import logging
from flask_mail import Message

LOG = logging.getLogger(__name__)


def notify_match_internal(database, match_obj, admin_email, mail):
    """Send an email to patient contacts after an internal match

    Args:
        database(pymongo.database.Database): patientMatcher database
        match_obj(dict): an object containing both query patient(dict) and matching results(list)
        admin_email(str): email of the server admin
        mail(flask_mail.Mail): an email instance
    """
    # Internal matching can be triggered by a patient in the same database or by a patient on a connected node.
    # In the first case notify both querier contact and contacts in the result patients.
    # in the second case notify only contacts from patients in the results list.

    sender = admin_email
    patient_id = None
    patient_label = None
    results = None
    recipient = None
    email_subject = 'MatchMaker Exchange: new patient match available.'
    email_body = None

    # check if query patient belongs to patientMatcher database:
    internal_patient = database['patients'].find({'_id':match_obj['data']['patient']['id']}).count()
    if internal_patient:
        #If patient used for the search is on patientMatcher database, notify querier as well:
        patient_id = match_obj['data']['patient']['id']
        patient_label = match_obj['data']['patient'].get('label')
        results = match_obj['results']
        recipient = match_obj['data']['patient']['contact']['href'][7:]
        email_body = active_match_email_body(patient_id, results, patient_label, external_match=False)
        LOG.info('Sending an internal match notification for query patient with ID:{0}. Patient contact: {1}'.format(patient_id, recipient))

        kwargs = dict(subject=email_subject, html=email_body, sender=sender, recipients=[recipient])
        message = Message(**kwargs)
        # send email using flask_mail
        try:
            mail.send(message)
        except Exception as err:
            LOG.error('An error occurred while sending an internal match notification: {}'.format(err))


    # Loop over the result patients and notify their contact about the matching with query patient
    for result in match_obj['results']:
        patient_id = result['patient']['id']
        patient_label =  result['patient'].get('label')
        recipient = result['patient']['contact']['href'][7:]
        email_body = passive_match_email_body(patient_id, patient_label)
        LOG.info('Sending an internal match notification for match result with ID {}'.format(patient_id))

        kwargs = dict(subject=email_subject, html=email_body, sender=sender, recipients=[recipient])
        message = Message(**kwargs)
        # send email using flask_mail
        try:
            mail.send(message)
        except Exception as err:
            LOG.error('An error occurred while sending an internal match notification: {}'.format(err))


def notify_match_external(match_obj, admin_email, mail):
    """Send an email to patients contacts to notify a match on external nodes

    Args:
        match_obj(dict): an object containing both query patient(dict) and matching results(list)
        admin_email(str): email of the server admin
        mail(flask_mail.Mail): an email instance
    """

    sender = admin_email
    patient_id = match_obj['data']['patient']['id']
    patient_label = match_obj['data']['patient'].get('label')
    results = match_obj['results']
    recipient = match_obj['data']['patient']['contact']['href'][7:]
    email_subject = 'MatchMaker Exchange: new patient match available.'
    email_body = active_match_email_body(patient_id, results, patient_label, external_match=True)
    LOG.info('Sending an external match notification for query patient with ID {0}. Patient contact: {1}'.format(patient_id, recipient))

    kwargs = dict(subject=email_subject, html=email_body, sender=sender, recipients=[recipient])
    message = Message(**kwargs)
    # send email using flask_mail
    try:
        mail.send(message)
    except Exception as err:
        LOG.error('An error occurred while sending an external match notification: {}'.format(err))



def active_match_email_body(patient_id, results, patient_label=None, external_match=False):
    """Returns the body message of the notification email when the patient was used as query patient

    Args:
        patient_id(str): the ID of the patient submitted by the  MME user which will be notified
        external_match(bool): True == match in connected nodes, False == match with other patients in database
        results(list): a list of patients which match with the patient whose contact is going to be notified
        patient_label(str): the label of the patient submitted by the  MME user which will be notified (not mandatory field)


    Returns:
        html(str): the body message
    """
    search_type = 'against the internal database of MatchMaker patients'
    if external_match:
        search_type = 'against external nodes connected to MatchMaker'

    html = """
        ***This is an automated message, please do not reply to this email.***<br><br>
        <strong>MatchMaker Exchange patient matching notification:</strong><br><br>
        Patient with ID <strong>{0}</strong>, label <strong>{1}</strong> was recently used in a search {2}.
        This search returned <strong>{3} potential matche(s)</strong>.<br><br>
        For security reasons match results and patient contacts are not disclosed in this email.<br>
        Please contact the service provider or connect to the portal you used to submit the data to review these results.
        <br><br>
        Kind regards,<br>
        The PatienMatcher team
    """.format(patient_id, patient_label, search_type, len(results))

    return html


def passive_match_email_body(patient_id, patient_label=None):
    """Returns the body message of the notification email when the patient was used as query patient

    Args:
        patient_id(str): the ID of the patient submitted by the  MME user which will be notified
        patient_label(str): the label of the patient submitted by the  MME user which will be notified (not mandatory field)

    Returns:
        html(str): the body message
    """

    html = """
        ***This is an automated message, please do not reply.***<br>
        <strong>MatchMaker Exchange patient matching notification:</strong><br><br>
        Patient with <strong>ID {0}</strong>,<strong> label {1}</strong> was recently returned as a match result
        in a search performed using a patient stored in the same MatchMaker node.
        For security reasons match results and patient contacts are not disclosed in this email.<br>
        Please contact the service provider or connect to the portal you used to submit the data to review these results.
        <br><br>
        Kind regards,<br>
        The PatienMatcher team
    """.format(patient_id, patient_label)

    return html
