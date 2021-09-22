from patientMatcher.cli.commands import cli


def test_cli_update_resources(mock_app):

    runner = mock_app.test_cli_runner()

    # run resources update command with --test flag:
    result = runner.invoke(cli, ["update", "resources", "--test"])
    assert result.exit_code == 0
