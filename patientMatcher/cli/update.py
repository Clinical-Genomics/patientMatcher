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
@click.option("--href", type=click.STRING, required=False, help="Contact's href")
@click.option("--email", type=click.STRING, required=False, help="Contact's email")
@click.option("--new-href", type=click.STRING, required=False, help="New href")
@click.option("--new-email", type=click.STRING, required=False, help="New email")
@click.option("--new-name", type=click.STRING, required=False, help="New name")
@click.option("--new-institution", type=click.STRING, required=False, help="New institution")
def contact(href, email, new_href, new_email, new_name, new_institution):
    """Update contact person for a group of patients."""

    if bool(href) == bool(email):
        raise click.UsageError("You must provide EITHER --href or --email")

    if not any([new_href, new_email, new_name, new_institution]):
        click.echo(
            f"Provide at least a field you wish to update: --new-href / --new-email / --new-name / --new-institution"
        )
        return

    if href:
        query = {"contact.href": {"$regex": href}}
    elif email:
        query = {"contact.email": email}

    database = current_app.db
    matching_patients = patients(database=database, match_query=query)
    matching_contacts = list(matching_patients.distinct("contact.href"))

    if len(matching_contacts) == 0:
        click.echo(f"No patients found with query '{query}'")
        return
    if len(matching_contacts) > 1:
        click.echo(
            f"Your search for contact query '{query}' is returning more than one patients' contact.\nPlease restrict your search by typing a different href/email."
        )
        return

    set_options = {}
    if new_href:
        if bool(EMAIL_REGEX.match(new_href)) is True and "mailto:" not in new_href:
            new_href = ":".join(["mailto", new_href])

        if href_validate(new_href) is False:
            LOG.error(
                "Provided href does not have a valid schema. Provide either a URL (http://.., https://..) or an email address (mailto:..)"
            )
            return
        set_options["contact.href"] = new_href

    if new_email:
        set_options["contact.email"] = new_email
    if new_name:
        set_options["contact.name"] = new_name
    if new_institution:
        set_options["contact.institution"] = new_institution

    if click.confirm(
        f"{len(list(matching_patients))} patients will be updated with contact info:{set_options}. Confirm?",
        abort=True,
    ):
        result = database.patients.update_many(query, {"$set": set_options})
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
