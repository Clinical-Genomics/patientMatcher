from patientMatcher.cli.commands import cli


def test_cli_add_demo_data(mock_app, database, mock_symbol_2_ensembl, monkeypatch):
    """Test the class that adds demo data"""

    # GIVEN a mocked Ensembl REST API for conversion of gene symbols to Ensembl IDs
    class MockResponse(object):
        def __init__(self, url):
            self.status_code = 200
            self.gene_symbol = url.split("homo_sapiens/")[1].split("?")[0]

        def json(self):
            return [{"id": self.gene_symbol, "type": "gene"}]

    def mock_get(url, headers):
        return MockResponse(url)

    runner = mock_app.test_cli_runner()

    # make sure that "patients" collection is empty
    assert database["patients"].find_one() is None

    # run the load demo command without the -compute_phenotypes flag
    result = runner.invoke(cli, ["add", "demodata"])
    assert result.exit_code == 0

    # check that demo patients are inserted into database
    demo_patients = database["patients"].find()
    assert len(list(demo_patients)) == 50

    # check that genomic features contain genes described by HGNC gene symbols and Ensmbl IDs
    assert demo_patients[0]["genomicFeatures"][0]["gene"]["id"]
    assert demo_patients[0]["genomicFeatures"][0]["gene"]["_geneName"]

    # check that one demo client has been created
    assert database["clients"].find_one()


def test_cli_add_client(mock_app, database, test_client):

    # make sure that "clients" collection is empty
    assert database["client"].find_one() is None

    # test add a server using the app cli
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli,
        [
            "add",
            "client",
            "-id",
            test_client["_id"],
            "-token",
            test_client["auth_token"],
            "-url",
            test_client["base_url"],
        ],
    )

    assert result.exit_code == 0
    assert "Inserted client" in result.output

    # check that the server was added to the "nodes" collection
    assert database["clients"].find_one()

    # Try adding the client again
    result = runner.invoke(
        cli,
        [
            "add",
            "client",
            "-id",
            test_client["_id"],
            "-token",
            test_client["auth_token"],
            "-url",
            test_client["base_url"],
        ],
    )
    assert result.exit_code == 0
    # And you should get an abort message
    assert "Aborted" in result.output
    # And number of clients in database should stay the same
    results = database["clients"].find()
    assert len(list(results)) == 1


def test_cli_add_node(mock_app, database, test_node):
    # make sure that "nodes" collection is empty
    assert database["nodes"].find_one() is None

    # test add a server using the app cli
    runner = mock_app.test_cli_runner()
    result = runner.invoke(
        cli,
        [
            "add",
            "node",
            "-id",
            test_node["_id"],
            "-label",
            "This is a test node",
            "-token",
            test_node["auth_token"],
            "-matching_url",
            test_node["matching_url"],
            "-accepted_content",
            test_node["accepted_content"],
        ],
    )
    assert result.exit_code == 0
    assert "Inserted node" in result.output

    # check that the server was added to the "nodes" collection
    assert database["nodes"].find_one()

    # Try adding the node again
    result = runner.invoke(
        cli,
        [
            "add",
            "node",
            "-id",
            test_node["_id"],
            "-label",
            "This is a test node",
            "-token",
            test_node["auth_token"],
            "-matching_url",
            test_node["matching_url"],
            "-accepted_content",
            test_node["accepted_content"],
        ],
    )
    assert result.exit_code == 0
    # And you should get an abort message
    assert "Aborted" in result.output
    # And number of nodes in database should stay the same
    results = database["nodes"].find()
    assert len(list(results)) == 1
