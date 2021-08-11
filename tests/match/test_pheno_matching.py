# -*- coding: utf-8 -*-

from patientMatcher.match.phenotype_matcher import match, similarity_wrapper
from patientMatcher.parse.patient import mme_patient
from patientMatcher.resources import path_to_hpo_terms, path_to_phenotype_annotations
from patientMatcher.server.extensions import diseases, hpo, hpoic
from patientMatcher.utils.patient import Patient

PHENOTYPE_ROOT = "HP:0000118"


def test_patient_similarity_wrapper(mock_app):
    """Test the function that calculates the HPO similarity between 2 patients"""

    assert hpo
    assert diseases
    assert hpoic

    query_p_terms = [
        "HP:0008058",
        "HP:0007033",
        "HP:0002194",
        "HP:0002281",
    ]  # nervous system - related HPO terms

    # test wrapper by providing same terms for query patient and match patient:
    score = similarity_wrapper(
        hpoic=hpoic,
        hpo=hpo,
        max_hpo_score=1.0,
        hpo_terms_q=query_p_terms,
        hpo_terms_m=query_p_terms,
    )
    # score should be something like 0.9999999999999999
    assert round(score, 12) == 1

    match_p_terms = ["HP:0008058", "HP:0007033", "HP:0002194"]

    # test wrapper by providing almost the same terms for query patient and match patient:
    related_pheno_score = similarity_wrapper(
        hpoic=hpoic,
        hpo=hpo,
        max_hpo_score=1.0,
        hpo_terms_q=query_p_terms,
        hpo_terms_m=match_p_terms,
    )
    # similarity score should be lower, but still around 1
    assert round(related_pheno_score, 2) < score
    assert related_pheno_score > 0.8

    # provide completely different HPO terms for matching patient
    match_p_terms = ["HP:0003002", "HP:0000218"]  # breast cancer and high palate phenotypes
    unrelated_pheno_score = similarity_wrapper(
        hpoic=hpoic,
        hpo=hpo,
        max_hpo_score=1.0,
        hpo_terms_q=query_p_terms,
        hpo_terms_m=match_p_terms,
    )
    # then unrelated_pheno_score should be almost 0
    assert round(unrelated_pheno_score, 2) == 0

    # but still a positive number
    assert unrelated_pheno_score > 0


def test_phenotype_matching(gpx4_patients, database):
    """test the algorithm that compares the phenotype of a query patient against the database"""

    # insert 2 test patients into test database
    for patient in gpx4_patients:
        database["patients"].insert_one(patient)
    assert len(list(database["patients"].find())) == 2

    query_patient = gpx4_patients[0]
    assert query_patient

    # this patient has HPO terms and OMIM diagnosis
    formatted_patient = mme_patient(query_patient)
    assert len(formatted_patient["features"]) > 0
    assert len(formatted_patient["disorders"]) > 0

    matches_HPO_OMIM = match(
        database, 0.75, formatted_patient["features"], formatted_patient["disorders"]
    )
    assert len(matches_HPO_OMIM.keys()) == 2
    for key, value in matches_HPO_OMIM.items():
        assert "patient_obj" in value
        assert value["pheno_score"] > 0

    features = formatted_patient["features"]
    disorders = formatted_patient["disorders"]
    # remove HPO terms from the query patient, test that the algorithm works anyway
    # because matching will use OMIM disorders
    formatted_patient["features"] = []
    matches_OMIM = match(
        database, 0.75, formatted_patient["features"], formatted_patient["disorders"]
    )
    assert len(matches_OMIM.keys()) > 0 and len(matches_OMIM.keys()) < 50
    for key, value in matches_OMIM.items():
        assert "patient_obj" in value
        assert value["pheno_score"] > 0

    # remove the OMIM diagnosis from patient object. The algorithm should work
    # but it shouldn't return any match
    formatted_patient["disorders"] = []
    matches_no_phenotypes = match(
        database, 0.75, formatted_patient["features"], formatted_patient["disorders"]
    )
    assert len(matches_no_phenotypes.keys()) == 0

    # Add again features. The algorithm works again because HPO terms will be used
    formatted_patient["features"] = features
    matches_HPO = match(
        database, 0.75, formatted_patient["features"], formatted_patient["disorders"]
    )
    assert len(matches_HPO.keys()) == 2
    for key, value in matches_HPO.items():
        assert "patient_obj" in value
        assert value["pheno_score"] > 0

    # make sure that matches obtained when OMIM and HPO terms are present are more or equal than
    # when either of these phenotype terms is present by itself
    assert len(matches_HPO_OMIM.keys()) >= len(matches_OMIM.keys())
    assert len(matches_HPO_OMIM.keys()) >= len(matches_HPO.keys())
