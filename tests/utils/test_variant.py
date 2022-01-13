import responses
from patientMatcher.utils.variant import liftover


@responses.activate
def test_liftover_37_38():
    """Test variant liftover from GRCh37 to GRCh38"""

    # WHEN sending a liftover request with suitable coordinates in genome build 37
    chromosome = "X"
    start = 1000000
    end = 1000000

    # GIVEN a patched liftover Ensembl service
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/{chromosome}:{start}..{end}/GRCh38?content-type=application/json",
        json={
            "mappings": [
                {
                    "original": {
                        "assembly": "GRCh37",
                        "end": 1000000,
                        "coord_system": "chromosome",
                        "seq_region_name": "X",
                        "start": 1000000,
                        "strand": 1,
                    },
                    "mapped": {
                        "strand": 1,
                        "start": 1039265,
                        "seq_region_name": "X",
                        "end": 1039265,
                        "coord_system": "chromosome",
                        "assembly": "GRCh38",
                    },
                }
            ]
        },
        status=200,
    )

    # THEN the service should return valid mappings
    mappings = liftover("GRCh37", chromosome, start, end)

    # Each mapping should have the expected output format
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)
    for item in ["assembly", "seq_region_name", "start", "end"]:
        assert mappings[0]["mapped"][item]

    # And genome assembly should be GRCh38
    assert mappings[0]["mapped"]["assembly"] == "GRCh38"


@responses.activate
def test_liftover_38_37():
    """Test variant liftover from GRCh38 to GRCh37"""

    # WHEN sending a liftover request with suitable coordinates in genome build 38
    chromosome = "X"
    start = 1039265
    end = 1039265

    # GIVEN a patched liftover Ensembl service
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh38/{chromosome}:{start}..{end}/GRCh37?content-type=application/json",
        json={
            "mappings": [
                {
                    "original": {
                        "seq_region_name": "X",
                        "end": 1039265,
                        "assembly": "GRCh38",
                        "coord_system": "chromosome",
                        "strand": 1,
                        "start": 1039265,
                    },
                    "mapped": {
                        "seq_region_name": "X",
                        "end": 1000000,
                        "assembly": "GRCh37",
                        "strand": 1,
                        "coord_system": "chromosome",
                        "start": 1000000,
                    },
                },
                {
                    "original": {
                        "assembly": "GRCh38",
                        "seq_region_name": "X",
                        "end": 1039265,
                        "start": 1039265,
                        "strand": 1,
                        "coord_system": "chromosome",
                    },
                    "mapped": {
                        "seq_region_name": "HG480_HG481_PATCH",
                        "end": 1000000,
                        "assembly": "GRCh37",
                        "strand": 1,
                        "coord_system": "chromosome",
                        "start": 1000000,
                    },
                },
            ]
        },
        status=200,
    )

    # THEN the service should return valid mappings
    mappings = liftover("GRCh38", chromosome, start, end)

    # Each mapping should have the expected output format
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)

    for item in ["assembly", "seq_region_name", "start", "end"]:
        assert mappings[0]["mapped"][item]

    # And genome assembly should be GRCh37
    assert mappings[0]["mapped"]["assembly"] == "GRCh37"


@responses.activate
def test_liftover_MT_variant():
    """Test liftover for a mitochondrial variant from GRCh37 to GRCh38"""

    # GIVEN a mitochondrial variant
    chromosome = "MT"
    start = 7278
    end = 7278

    # GIVEN a patched liftover Ensembl service
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/{chromosome}:{start}..{end}/GRCh38?content-type=application/json",
        json={
            "mappings": [
                {
                    "mapped": {
                        "strand": 1,
                        "end": 7278,
                        "assembly": "GRCh38",
                        "coord_system": "chromosome",
                        "seq_region_name": "MT",
                        "start": 7278,
                    },
                    "original": {
                        "strand": 1,
                        "seq_region_name": "MT",
                        "start": 7278,
                        "end": 7278,
                        "assembly": "GRCh37",
                        "coord_system": "chromosome",
                    },
                }
            ]
        },
        status=200,
    )

    # THEN the service should return valid mappings
    mappings = liftover("GRCh37", chromosome, start, end)

    # Each mapping should have the expected output format
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)
    for item in ["assembly", "seq_region_name", "start", "end"]:
        assert mappings[0]["mapped"][item]

    # And genome assembly should be GRCh38
    assert mappings[0]["mapped"]["assembly"] == "GRCh38"


@responses.activate
def test_liftover_bad_request():
    """Test variant liftover with non-valid request params"""

    # WHEN sending a liftover request with non-standard chromosome (M instead of MT)
    chromosome = "M"
    start = 7278
    end = 7278

    # GIVEN a patched liftover Ensembl service
    responses.add(
        responses.GET,
        f"https://grch37.rest.ensembl.org/map/human/GRCh37/{chromosome}:{start}..{end}/GRCh38?content-type=application/json",
        json={"error": "'No slice found for M on coord_system chromosome and assembly GRCh37'"},
        status=200,
    )

    # THEN the service should not return mappings
    mappings = liftover("GRCh37", chromosome, start, end)
    assert mappings is None
