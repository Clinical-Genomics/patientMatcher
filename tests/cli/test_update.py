from patientMatcher.cli.commands import cli


def test_update_resources(mock_app):
    """Test the command that updates the database resources (diseases and HPO terms)"""
    runner = mock_app.test_cli_runner()

    # run resources update command with --test flag:
    result = runner.invoke(cli, ["update", "resources", "--test"])
    assert result.exit_code == 0


def test_update_contact(mock_app, gpx4_patients):
    """Test the command to bulk-update patients contact"""

    runner = mock_app.test_cli_runner()
    patients_collection = mock_app.db.patients

    # GIVEN a database with some patients
    patients_collection.insert_many(gpx4_patients)
    test_patients = patients_collection.find()
    # Sharing a contact information
    contacts = test_patients.distinct("contact.href")
    assert len(contacts) == 1

    # WHEN their contact info is updated using the cli
    new_href = "new.contact@mail.com"
    result = runner.invoke(
        cli,
        [
            "update",
            "contact",
            "-old-href",
            contacts[0],
            "-href",
            new_href,
            "-name",
            "New Name",
            "-institution",
            "Test Institution",
        ],
        input="y",
    )

    # THEN the config info should be updated
    updated_patient = patients_collection.find({"contact.href": new_href})
    assert len(list(updated_patient)) > 0
