#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import click
from flask import Flask, current_app
from flask.cli import FlaskGroup, routes_command, run_command, with_appcontext
from flask_mail import Message
from patientMatcher import __version__
from patientMatcher.server import create_app

from .add import add
from .remove import remove
from .update import update


def create_basic_app():
    return Flask(__name__)


# Extend FlaskGroup to choose if the app should be instantiated or not when launching the cli
class CustomFlaskGroup(FlaskGroup):
    # If user has typed --help or launched the cli without arguments
    def __init__(self, *args, **kwargs):
        if (
            "--help" in sys.argv or len(sys.argv) == 1
        ):  # No need to create the real app to show help and exit
            super().__init__(
                create_app=create_basic_app,
                **kwargs,
            )

        else:  # Else create an app object connected to the database
            super().__init__(create_app=create_app, **kwargs)

        super().add_command(run_command)
        super().add_command(routes_command)

    def get_command(self, ctx, name):
        return super(CustomFlaskGroup, self).get_command(ctx, name)

    def list_commands(self, ctx):
        return super(CustomFlaskGroup, self).list_commands(ctx)


@click.version_option(__version__)
@click.group(
    cls=CustomFlaskGroup,
)
@click.pass_context
def cli(ctx):
    """Base command for invoking the command line"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@click.group()
def test():
    """Test server using CLI"""
    pass


@test.command()
@with_appcontext
def name():
    """Returns the app name, for testing purposes, mostly"""
    app_name = current_app.name.split(".")[0]
    click.echo(app_name)
    return app_name


@test.command()
@with_appcontext
@click.option(
    "-r",
    "--recipient",
    type=click.STRING,
    nargs=1,
    required=True,
    help="Email address to send the test email to",
)
def email(recipient):
    """Sends a test email using config settings"""
    click.echo(recipient)

    subj = "Test email from patientMatcher"
    body = """
        ***This is an automated message, please do not reply to this email.***<br><br>
        If you receive this email it means that email settings are working fine and the
        server will be able to send match notifications.<br>
        A mail notification will be sent when:<br>
        <ul>
            <li>A patient is added to the database and the add request triggers a search
            on external nodes producing at least one result (/patient/add endpoint).</li>

            <li>An external search is actively performed on connected nodes and returns
            at least one result (/match/external/<patient_id> endpoint).</li>

            <li>The server is interrogated by an external node and returns at least one
            result match (/match endpoint). In this case a match notification is sent to
             each contact of the result matches.</li>

            <li>An internal search is submitted to the server using a patient from the
            database (/match endpoint) and this search returns at least one match.
            In this case contact users of all patients involved will be notified
            (contact from query patient and contacts from the result patients).</li>
        </ul>
        <br>
        You can stop server notification any time by commenting the MAIL_SERVER parameter in
        config file and rebooting the server.
        <br><br>
        Kind regards,<br>
        The PatientMatcher team
    """
    kwargs = dict(
        subject=subj,
        html=body,
        sender=current_app.config.get("MAIL_USERNAME"),
        recipients=[recipient],
    )
    message = Message(**kwargs)
    try:
        current_app.mail.send(message)
        click.echo("Mail correctly sent. Check your inbox!")
    except Exception as err:
        click.echo('An error occurred while sending test email: "{}"'.format(err))


cli.add_command(test)
test.add_command(name)
test.add_command(email)
cli.add_command(add)
cli.add_command(update)
cli.add_command(remove)
