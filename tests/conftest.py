# -*- coding: utf-8 -*-
import json

import mongomock
import pytest
import responses
from patientMatcher.resources import path_to_benchmark_patients
from patientMatcher.server import create_app

DATABASE = "testdb"
TEST_MAILTO = "mailto:test_contact@email.com"

HGNC_SYMBOLS_2_ENSEMBL_IDS = {
    "AAGAB": "ENSG00000103591",
    "LAMA1": "ENSG00000101680",
    "SNRPB": "ENSG00000101680",
    "NGLY1": "ENSG00000151092",
    "LIMS2": "ENSG00000072163",
    "KARS": "ENSG00000065427",
    "GUCY2C": "ENSG00000070019",
    "GPX4": "ENSG00000167468",
    "STAMBP": "ENSG00000124356",
    "HSD17B4": "ENSG00000133835",
    "GARS": "ENSG00000106105",
    "ALDH6A1": "ENSG00000119711",
    "EFTUD2": "ENSG00000108883",
    "SYNJ1": "ENSG00000159082",
    "IARS2": "ENSG00000067704",
    "GRIN2A": "ENSG00000183454",
    "WDR62": "ENSG00000075702",
    "ATP1A3": "ENSG00000272584",
    "SKI": "ENSG00000157933",
    "PIK3R1": "ENSG00000145675",
    "THOC6": "ENSG00000131652",
    "G6PC3": "ENSG00000141349",
    "TTC7A": "ENSG00000068724",
    "SGOL1": "ENSG00000129810",
}


@pytest.fixture
def mock_symbol_2_ensembl():
    return HGNC_SYMBOLS_2_ENSEMBL_IDS


class MockMail:
    _send_was_called = False
    _message = None

    def send(self, message):
        self._send_was_called = True
        self._message = message


@pytest.fixture
def mock_app(database, pymongo_client):
    app = create_app()
    app.db = database
    app.client = pymongo_client
    return app


@pytest.fixture
def mock_mail():
    return MockMail()


@pytest.fixture
def mock_sender():
    return "mock_sender"


@pytest.fixture(scope="function")
def pymongo_client(request):
    """Get a client to the mongo database"""
    mock_client = mongomock.MongoClient()

    def teardown():
        mock_client.drop_database(DATABASE)

    request.addfinalizer(teardown)
    return mock_client


@pytest.fixture(scope="function")
def database(request, pymongo_client):
    """Get an adapter connected to mongo database"""
    mongo_client = pymongo_client
    database = mongo_client[DATABASE]
    return database


@pytest.fixture(scope="function")
def demo_data_path():
    return path_to_benchmark_patients


@pytest.fixture(scope="function")
def test_client():
    """Returns a test client object"""
    client = {
        "_id": "client_1",
        "auth_token": "superSecretToken",
        "base_url": "https://test_node_institution.com",
        "contact": "test_client@email.com",
    }
    return client


@pytest.fixture(scope="function")
def test_node():
    """Returns a test client object"""
    node = {
        "_id": "node_1",
        "label": "Test node description",
        "auth_token": "superSecretToken",
        "matching_url": "https://test_node/match/",
        "accepted_content": "application/vnd.ga4gh.matchmaker.v1.0+json",
        "contact": "test_node_user@email.com",
    }
    return node


@pytest.fixture(scope="function")
def entrez_gene_patient():
    """Returns a test patient with an entrez gene ID"""
    patient = {
        "contact": {
            "href": "mailto:someuser@mail.com",
            "institution": "Test institution",
            "name": "Test user",
        },
        "disorders": [],
        "features": [
            {"id": "HP:0001263", "label": "Global developmental delay", "observed": "yes"},
            {"id": "HP:0000252", "label": "Microcephaly", "observed": "yes"},
        ],
        "genomicFeatures": [
            {
                "gene": {"id": "3735"},
                "type": {"id": "SO:0001583", "label": "MISSENSE"},
                "variant": {
                    "alternateBases": "A",
                    "assembly": "GRCh37",
                    "end": 75665092,
                    "referenceBases": "G",
                    "referenceName": "16",
                    "start": 75665091,
                },
                "zygosity": 1,
            }
        ],
        "id": "P0001013",
        "label": "169_1-test",
    }
    return patient


@pytest.fixture(scope="function")
def match_objs():
    """Mock the results of an internal and an external match"""
    matches = [
        {  # External match where test_patient is the query and with results
            "_id": "match_1",
            "has_matches": True,
            "data": {"patient": {"id": "P0001058", "contact": {"href": TEST_MAILTO}}},
            "results": [
                {
                    "node": {"id": "test_node1", "label": "Test Node 1"},
                    "patients": [{"patient": {"id": "patient1"}}, {"patient": {"id": "patient2"}}],
                },
                {
                    "node": {"id": "test_node2", "label": "Test Node 2"},
                    "patients": [{"patient": {"id": "patient3"}}],
                },
            ],
            "match_type": "external",
        },
        {  # Internal match where test_patient is the query and there are no results
            "_id": "match_2",
            "has_matches": False,
            "data": {
                "patient": {"id": "P0001058"},
                "contact": {"href": TEST_MAILTO},
            },
            "results": [
                {
                    "node": {"id": "patientMatcher", "label": "patientMatcher server"},
                    "patients": [{"patient": {"id": "int_patient_id"}}],
                }
            ],
            "match_type": "internal",
        },
        {  #  Internal match where test_patient is among results
            "_id": "match_3",
            "has_matches": True,
            "data": {
                "patient": {
                    "id": "external_patient_1",
                    "contact": {"href": TEST_MAILTO},
                }
            },
            "results": [
                {
                    "node": {"id": "test_node1", "label": "Test Node 1"},
                    "patients": [
                        {
                            "patient": {
                                "id": "P0001058",
                                "contact": {"href": "mailto:test_contact2@email.com"},
                            }
                        }
                    ],
                }
            ],
            "match_type": "internal",
        },
    ]
    return matches


@pytest.fixture()
def patient_37():
    """A patient with a variant in genome assembly GRCh38"""

    patient = {
        "patient": {
            "id": "patient_id",
            "contact": {"name": "Contact Name", "href": "mailto:contact_name@mail.com"},
            "features": [{"id": "HP:0009623"}],
            "genomicFeatures": [
                {
                    "gene": {"id": "GUCY2C"},
                    "variant": {
                        "assembly": "GRCh37",
                        "referenceName": "12",
                        "start": 14794075,
                        "end": 14794076,
                        "referenceBases": "C",
                        "alternateBases": "T",
                    },
                }
            ],
        }
    }
    return patient


@pytest.fixture(scope="function")
def gpx4_patients(json_patients):
    """Return all patients with variants in GPX4 gene"""

    patient_list = []

    for patient in json_patients:
        gpx4 = False
        if patient.get("genomicFeatures") is None:
            continue
        for g_feature in patient["genomicFeatures"]:
            if g_feature["gene"]["id"] == "GPX4":
                gpx4 = True
        if gpx4:
            patient_list.append(patient)
    return patient_list


@pytest.fixture(scope="function")
def json_patients(demo_data_path):
    """Returns a list of 50 MME test patients from demo data"""
    patients = {}
    with open(demo_data_path) as json_data:
        patients = json.load(json_data)
    return patients


@pytest.fixture()
def mocked_ensemble_responses():
    """Provides mock responses from Ensembl services"""
    with responses.RequestsMock() as mock:
        # a mocked Ensembl REST API converting gene symbol to Ensembl ID
        responses.add(
            responses.GET,
            f"https://grch37.rest.ensembl.org/xrefs/symbol/homo_sapiens/GPX4?external_db=HGNC",
            json=[{"id": "ENSG00000167468", "type": "gene"}],
            status=200,
        )
        # a mocked Ensembl gene lookup service:
        responses.add(
            responses.GET,
            f"https://grch37.rest.ensembl.org/lookup/id/ENSG00000167468",
            json=[{"display_name": "GPX4"}],
            status=200,
        )
        # a mocked liftover service:
        responses.add(
            responses.GET,
            f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1105813..1105814/GRCh38?content-type=application/json",
            json=[],
            status=200,
        )
        # Another mocked liftover service:
        responses.add(
            responses.GET,
            f"https://grch37.rest.ensembl.org/map/human/GRCh37/19:1106232..1106238/GRCh38?content-type=application/json",
            json=[],
            status=200,
        )

        yield mock
