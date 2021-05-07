from patientMatcher.server.extensions import diseases, hpo


def test_hpo(mock_app):
    """Test the extension handling the HPO terms"""

    root_term = "HP:0000001"
    obsolete_term = "HP:0000057"

    # GIVEN the hpo extension of an app
    assert hpo
    # THEN the hpo should countain HPO terms in a dictionary
    assert isinstance(hpo.hps, dict)
    # THEN the HPO should contain ontology root term
    assert hpo[root_term]
    assert hpo[root_term].id == root_term

    # IT should also contain obsolete terms linked to non-obsolete terms
    assert hpo[obsolete_term].id != obsolete_term
    assert hpo[obsolete_term].parents
    assert hpo[obsolete_term]._parent_hps


def test_diseases(mock_app):
    """Test the extension handling disease terms"""

    # GIVEN the hpo extension of an app
    assert diseases

    # THEN the hpo should countain disease terms in a dictionary
    assert isinstance(diseases.diseases, dict)

    # GIVEN a specific term
    test_db = "OMIM"
    test_term = 201180
    # Each dictionary key should contain the expected fields
    assert diseases.diseases[(test_db, test_term)].db == test_db
    assert diseases.diseases[(test_db, test_term)].id == test_term
    assert diseases.diseases[(test_db, test_term)].phenotype_freqs
