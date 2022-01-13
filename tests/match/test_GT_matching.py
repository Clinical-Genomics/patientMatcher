# -*- coding: utf-8 -*-
import responses
from patientMatcher.match.genotype_matcher import match
from patientMatcher.parse.patient import mme_patient


@responses.activate
def test_genotype_matching(database, gpx4_patients):
    """Testing the genotyping matching algorithm"""

    # GIVEN a mocked Ensembl REST API:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/GPX4?external_db=HGNC",
        json=[{"id": "ENSG00000167468", "type": "gene"}],
        status=200,
    )

    # GIVEN a mocked Ensembl gene lookup service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/lookup/id/ENSG00000167468",
        json=[{"display_name": "GPX4"}],
        status=200,
    )

    # GIVEN a mocked liftover service:
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1105813..1105814/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1106232..1106238/GRCh38?content-type=application/json",
        json=[],
        status=200,
    )

    # load 2 test patients in mock database
    for patient in gpx4_patients:
        mme_pat = mme_patient(patient, True)  # convert gene symbol to ensembl
        database["patients"].insert_one(mme_pat).inserted_id

    # 2 patients should be inserted
    results = database["patients"].find({"genomicFeatures.gene.id": "ENSG00000167468"})
    assert len(list(results)) == 2

    # test matching of a patient (with variants in genes) against the demo patients in database
    proband_patient = mme_patient(gpx4_patients[0], True)

    # assert patient has genomic features
    gt_features = proband_patient["genomicFeatures"]
    assert len(gt_features) == 2  # should have 2 feature to match
    assert gt_features[0]["gene"]["id"] == "ENSG00000167468"

    # match features against database with 2 patients
    matches = match(database, gt_features, 0.5)
    assert len(matches.keys()) == 2  # 2 matching patients are returned

    for key, value in matches.items():
        # patient object should also be returned
        assert "patient_obj" in value

        # genotype score for each patient should be higher than 0
        assert value["geno_score"] > 0

    # make sure that the algorithm works even if a gene or a variant object is missing:
    # remove gene ID from first gt feature
    gt_features[0]["gene"]["id"] = ""
    matches = match(database, gt_features, 0.5)
    # same patient should be returned, because of variant matching instead
    assert len(matches) == 2

    # Remove variant object from second gt feature
    gt_features[1]["variant"] = None
    matches = match(database, gt_features, 0.5)
    # same patients should be returned, because of gene matching instead
    assert len(matches.keys()) == 2
