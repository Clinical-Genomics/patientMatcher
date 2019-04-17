# -*- coding: utf-8 -*-

def test_create_app(mock_app):
    """Tests the function that creates the app"""

    assert mock_app.client
    assert mock_app.db
