# -*- coding: utf-8 -*-

from patientMatcher.server import create_app

def test_create_app(database):
    """Tests the function that creates the app"""

    app = create_app()

    assert app.client
    assert app.db
