from patientMatcher.server.extensions import diseases, hpo


def test_hpo(mock_app):
    """Test the extension handling the HPO terms"""

    root_term = "HP:0000001"
    obsolete_term = "HP:0000057"

    # GIVEN the hpo extension of an app
    assert hpo
    # THEN the hpo should countain HPO terms in a dictionary
    assert type(hpo.hps) == dict
    # THEN the HPO should contain ontology root term
    assert hpo[root_term]

    # IT should also contain obsolete terms linked to non-obsolete terms
    assert hpo[obsolete_term].id != obsolete_term
    assert hpo[obsolete_term].parents
    assert hpo[obsolete_term]._parent_hps
