import responses
from patientMatcher.cli.commands import cli
from patientMatcher.constants import PHENOTYPE_TERMS


@responses.activate
def test_update_resources(mock_app):
    """Test the command that updates the database resources (diseases and HPO terms)"""

    # Given a mocked response from the servers containing the resources to be downloaded
    for key, item in PHENOTYPE_TERMS.items():

        local_resource_path = item["resource_path"]  # Resource on the local repo
        url = item["url"]  # Resource internet URL
        with open(local_resource_path, "r") as res:
            responses.add(
                responses.GET,
                url,
                body=res.read(),
                status=200,
                content_type="application/octet-stream",
                auto_calculate_content_length=True,
                stream=True,
            )

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
            "--old-href",
            contacts[0],
            "--href",
            new_href,
            "--name",
            "New Name",
            "--institution",
            "Test Institution",
        ],
        input="y",
    )
    assert result.exit_code == 0

    # THEN the config info should be updated
    updated_patient = patients_collection.find({"contact.href": ":".join(["mailto", new_href])})
    assert len(list(updated_patient)) > 0


def test_update_contact_no_href_match(mock_app, gpx4_patients):
    """Test the command to bulk-update patients contact when old contact href is not matching any patients"""

    runner = mock_app.test_cli_runner()
    patients_collection = mock_app.db.patients

    # GIVEN a database with some patients
    patients_collection.insert_many(gpx4_patients)
    test_patients = patients_collection.find()
    # Sharing a contact information
    contacts = test_patients.distinct("contact.href")
    assert len(contacts) == 1
    old_contact_href = contacts[0]

    # GIVEN a contact href without matches in the patients documents
    wrong_href = "some_href"
    assert wrong_href not in old_contact_href

    # WHEN their contact info is updated using the cli
    new_href = "new.contact@mail.com"
    result = runner.invoke(
        cli,
        [
            "update",
            "contact",
            "--old-href",
            wrong_href,
            "--href",
            new_href,
            "--name",
            "New Name",
            "--institution",
            "Test Institution",
        ],
    )
    assert result.exit_code == 0

    # THEN no patients contact should be updated
    assert patients_collection.find_one({"contact.href": ":".join(["mailto", new_href])}) is None


def test_update_contact_multiple_href_match(mock_app, gpx4_patients):
    """Test the command to bulk-update patients contact when old contact href is matching more than one patient contact"""

    runner = mock_app.test_cli_runner()
    patients_collection = mock_app.db.patients

    assert len(gpx4_patients) == 2
    # GIVEN a database with 2 patients with sligthly different contact href
    gpx4_patients[0]["contact"]["href"] = "test_1@mail.com"
    gpx4_patients[0]["contact"]["href"] = "test_2@mail.com"
    patients_collection.insert_many(gpx4_patients)

    # WHEN their contact info is updated using the cli but the search for the old href returns multiple contacts
    old_href = "test_"
    new_href = "test_3@mail.com"
    result = runner.invoke(
        cli,
        [
            "update",
            "contact",
            "--old-href",
            old_href,
            "--href",
            new_href,
            "--name",
            "New Name",
            "--institution",
            "Test Institution",
        ],
    )

    # THEN no patients contact should be updated
    assert patients_collection.find_one({"contact.href": ":".join(["mailto", new_href])}) is None
