#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

import click
from flask.cli import current_app, with_appcontext
from patientMatcher.parse.patient import EMAIL_REGEX, href_validate
from patientMatcher.utils.patient import patients
from patientMatcher.utils.update import update_resources

LOG = logging.getLogger(__name__)


@click.group()
def update():
    """Update patientMatcher resources"""
    pass


@update.command()
@with_appcontext
@click.option(
    "-o", "--old-href", type=click.STRING, nargs=1, required=True, help="Old contact href"
)
@click.option("-h", "--href", type=click.STRING, nargs=1, required=True, help="New contact href")
@click.option("-n", "--name", type=click.STRING, nargs=1, required=True, help="New contact name")
@click.option(
    "--institution", type=click.STRING, nargs=1, required=False, help="New contact institution"
)
def contact(old_href, href, name, institution):
    """Update contact person for a group of patients"""

    # If new contact is a simple email, add "mailto" schema
    if bool(EMAIL_REGEX.match(href)) is True and "mailto:" not in href:
        href = ":".join(["mailto", href])

    if href_validate(href) is False:
        LOG.error(
            "Provided href does not have a valid schema. Provide either a URL (http://.., https://..) or an email address (mailto:..)"
        )
        return

    database = current_app.db
    query = {"contact.href": {"$regex": old_href}}

    # Retrieving all patients matching the given old_href
    old_contact_patients = patients(database=database, match_query=query)
    # Retriving unique contacts for the above patients
    match_contacts = list(old_contact_patients.distinct("contact.href"))

    if len(match_contacts) == 0:
        click.echo(f"No patients found with contact URI '{old_href}'")
        return
    if len(match_contacts) > 1:
        click.echo(
            f"Your search for contact url '{old_href}' is returning more than one patients' contact: {match_contacts}.\nPlease restrict your search by typing a different href."
        )
        return
    # Search is returning only one contact, it's OK to use it for updating patients
    matches = list(old_contact_patients)
    new_contact = dict(href=href, name=name)
    if institution:
        new_contact["institution"] = institution

    if click.confirm(
        f"{len(matches)} patients with the old contact href '{matches[0]['contact']['href']}' will be updated with contact info:{new_contact}. Confirm?",
        abort=True,
    ):
        result = database.patients.update_many(query, {"$set": {"contact": new_contact}})
        click.echo(f"Contact information was updated for {result.modified_count} patients.")


@update.command()
@click.option("--test", help="Use this flag to test the function", is_flag=True)
def resources(test):
    """Updates HPO terms and disease ontology from the web.
    Specifically collect files from:
    http://purl.obolibrary.org/obo/hp.obo
    https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa
    """
    update_resources(test)
