from patientMatcher.utils.variant import liftover


def test_liftover_37_38():
    """Test variant liftover from GRCh37 to GRCh38"""

    # WHEN sending a liftover request with suitable coordinates in genome build 37
    chromosome = "X"
    start = 1000000
    end = 1000000

    # THEN the service should return valid mappings
    mappings = liftover("GRCh37", chromosome, start, end)

    # Each mapping should have the expected output format
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)
    for item in ["assembly", "seq_region_name", "start", "end"]:
        assert mappings[0]["mapped"][item]

    # And genome assembly should be GRCh38
    assert mappings[0]["mapped"]["assembly"] == "GRCh38"


def test_liftover_38_37():
    """Test variant liftover from GRCh38 to GRCh37"""

    # WHEN sending a liftover request with suitable coordinates in genome build 38
    chromosome = "X"
    start = 1039265
    end = 1039265

    # THEN the service should return valid mappings
    mappings = liftover("GRCh38", chromosome, start, end)

    # Each mapping should have the expected output format
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)

    for item in ["assembly", "seq_region_name", "start", "end"]:
        assert mappings[0]["mapped"][item]

    # And genome assembly should be GRCh37
    assert mappings[0]["mapped"]["assembly"] == "GRCh37"


def test_liftover_MT_variant():
    """Test liftover for a mitochondrial variant from GRCh37 to GRCh38"""

    # GIVEN a mitochondrial variant
    chromosome = "MT"
    start = 7278
    end = 7278

    # THEN the service should return valid mappings
    mappings = liftover("GRCh37", chromosome, start, end)

    # Each mapping should have the expected output format
    assert isinstance(mappings, list)
    assert isinstance(mappings[0], dict)
    for item in ["assembly", "seq_region_name", "start", "end"]:
        assert mappings[0]["mapped"][item]

    # And genome assembly should be GRCh38
    assert mappings[0]["mapped"]["assembly"] == "GRCh38"


def test_liftover_bad_request():
    """Test variant liftover with non-valid request params"""

    # WHEN sending a liftover request with non-standard chromosome (M instead of MT)
    chromosome = "M"
    start = 7278
    end = 7278

    # THEN the service should not return mappings
    mappings = liftover("GRCh37", chromosome, start, end)
    assert mappings is None
