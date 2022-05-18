# -*- coding: utf-8 -*-
import logging

from flask import current_app, jsonify
from jsonschema import ValidationError
from patientMatcher.__version__ import __version__
from patientMatcher.auth.auth import authorize
from patientMatcher.constants import STATUS_CODES
from patientMatcher.match.handler import external_matcher
from patientMatcher.parse.patient import EMAIL_REGEX, href_validate, mme_patient, validate_api
from patientMatcher.utils.delete import delete_by_query
from patientMatcher.utils.patient import patients
from patientMatcher.utils.stats import general_metrics

LOG = logging.getLogger(__name__)


def populate_index_data():
    """Populate the dictionary used to display the server index page"""
    data = dict(
        node_stats=metrics(),
        node_disclaimer=current_app.config.get("DISCLAIMER"),
        node_contacts=current_app.config.get("ADMINS"),
        connected_nodes=len(get_nodes(current_app.db)),
        software_version=__version__,
    )
    return data


def heartbeat(disclaimer):
    """Return a heartbeat as defined here:https://github.com/ga4gh/mme-apis/blob/master/heartbeat-api.md"""

    hbeat = {
        "heartbeat": {
            "production": current_app.config.get("TESTING", "True") in ["False", False],
            "version": __version__,
            "accept": [
                "application/vnd.ga4gh.matchmaker.v1.0+json",
                "application/vnd.ga4gh.matchmaker.v1.1+json",
            ],
        },
        "disclaimer": disclaimer,
    }
    return hbeat


def metrics():
    """return database metrics"""
    db_metrics = general_metrics(current_app.db)
    return db_metrics


def get_nodes(database):
    """Get all connected nodes as a list of objects with node_id and node_label as elements"""
    results = list(database["nodes"].find())
    nodes = []
    for node in results:
        nodes.append({"id": node["_id"], "description": node["label"]})
    return nodes


def patient(database, patient_id):
    """Return a mme-like patient from database by providing its ID"""
    query_patient = None
    query_result = list(patients(database=database, ids=[patient_id]))
    if query_result:
        query_patient = query_result[0]
    return query_patient


def match_external(database, query_patient, node=None):
    """Trigger an external patient matching for a given patient object"""
    # trigger the matching and save the matching id to variable
    matching_obj = external_matcher(database, query_patient, node)
    # save matching object to database only if there are results or error messages
    if matching_obj and (matching_obj.get("has_matches") or matching_obj.get("errors")):
        database["matches"].insert_one(matching_obj)
    return matching_obj


def check_request(database, request):
    """Check if request is valid, if it is return MME formatted patient
    Otherwise return error code.
    """

    # check that request is using a valid auth token
    if not authorize(database, request):
        LOG.warning("Request is not authorized")
        return 401

    try:  # make sure request has valid json data
        request_json = request.get_json(force=True)
    except Exception as err:
        LOG.warning("Json data in request is not valid:{}".format(err))
        return 400

    try:
        # validate json data against MME API
        validate_api(json_obj=request_json, is_request=True)
    except Exception as err:
        LOG.warning("Patient data does not conform to API:{}".format(err))
        return 422

    # validate and eventually fix patient's contact href
    contact_href = request_json["patient"]["contact"]["href"]

    # If new contact is a simple email, add "mailto" schema
    if bool(EMAIL_REGEX.match(contact_href)) is True and not "mailto:" in contact_href:
        contact_href = ":".join(["mailto", contact_href])
        request_json["patient"]["contact"]["href"] = contact_href

    if href_validate(contact_href) is False:
        LOG.warning(
            "Provided contact href does not have a valid schema - either a URL (http://.., https://..) or an email address (mailto:..)"
        )
        return 422

    formatted_patient = mme_patient(json_patient=request_json["patient"], convert_to_ensembl=True)
    return formatted_patient


def validate_response(matches):
    """Validates patient matching results before sending them away in a response"""

    try:  # validate json data against MME API
        validate_api(json_obj=matches, is_request=False)
    except ValidationError as err:
        LOG.info("Patient data does not conform to API:{}".format(err))
        return 422
    return matches


def bad_request(error_code):
    """Crete an automatic response based on custom error codes"""
    message = STATUS_CODES[error_code]["message"]
    resp = jsonify(message)
    resp.status_code = error_code
    return resp


def delete_patient(database, patient_id):
    """Remove a patient by ID"""
    message = ""

    # first delete all matches in database for this patient:
    query = {"data.patient.id": patient_id}
    deleted = delete_by_query(query, database, "matches")
    LOG.info("deleted {} matche/s triggered by this patient".format(deleted))

    query = {"_id": patient_id}
    deleted = delete_by_query(query, database, "patients")
    message = {}
    if deleted == 1:
        message["message"] = "Patient and its matches were successfully deleted from database"
    else:
        message["message"] = "ERROR. Could not delete a patient with ID {} from database".format(
            patient_id
        )
    return message
