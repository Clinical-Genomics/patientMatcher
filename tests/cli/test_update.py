import responses

from patientMatcher.cli.commands import cli
from patientMatcher.constants import PHENOTYPE_TERMS

CONTACT_HREF = "contact.href"
NEW_HREF = "http://test.com"
NEW_EMAIL = "new.email@mail.com"
NEW_NAME = "New Name"
TEST_INST = "Test Institution"


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


def test_update_contact_success(mock_app, gpx4_patients, monkeypatch):
    """Test updating a contact successfully"""

    runner = mock_app.test_cli_runner()
    patients_collection = mock_app.db.patients

    # GIVEN a database with patients
    patients_collection.insert_many(gpx4_patients)
    contacts = list(patients_collection.find().distinct(CONTACT_HREF))
    assert len(contacts) == 1

    # Mock click.confirm to always return True
    monkeypatch.setattr("click.confirm", lambda *args, **kwargs: True)

    # WHEN updating contact info
    result = runner.invoke(
        cli,
        [
            "update",
            "contact",
            "--href",
            contacts[0],
            "--new-href",
            NEW_HREF,
            "--new-email",
            NEW_EMAIL,
            "--new-name",
            NEW_NAME,
            "--new-institution",
            TEST_INST,
        ],
    )

    # THEN the update should succeed
    assert result.exit_code == 0
    assert "Contact information was updated" in result.output

    updated_patient = list(patients_collection.find({CONTACT_HREF: NEW_HREF}))
    assert len(updated_patient) > 0
    assert updated_patient[0]["contact"]["href"] == NEW_HREF
    assert updated_patient[0]["contact"]["email"] == NEW_EMAIL
    assert updated_patient[0]["contact"]["name"] == NEW_NAME
    assert updated_patient[0]["contact"]["institution"] == TEST_INST


def test_update_contact_validation(mock_app, gpx4_patients):
    """Test validations for contact CLI"""

    runner = mock_app.test_cli_runner()
    patients_collection = mock_app.db.patients

    patients_collection.insert_many(gpx4_patients)
    contacts = list(patients_collection.find().distinct(CONTACT_HREF))
    assert len(contacts) == 1

    # WHEN no update fields are provided
    result_no_update = runner.invoke(
        cli,
        ["update", "contact", "--href", contacts[0]],
    )
    assert result_no_update.exit_code == 0
    assert "Provide at least a field you wish to update" in result_no_update.output

    # WHEN both --href and --email are provided
    result_invalid = runner.invoke(
        cli,
        [
            "update",
            "contact",
            "--href",
            contacts[0],
            "--email",
            "some@email.com",
            "--new-name",
            "Name",
        ],
    )
    assert result_invalid.exit_code != 0
    assert "You must provide EITHER --href or --email" in result_invalid.output


def test_update_contact_no_href_match(mock_app, gpx4_patients):
    """
    Test the command when the provided old contact href does not match any patients.
    The command should not update anything and should output a message.
    """

    runner = mock_app.test_cli_runner()
    patients_collection = mock_app.db.patients

    # GIVEN a database with some patients
    patients_collection.insert_many(gpx4_patients)
    contacts = list(patients_collection.find().distinct(CONTACT_HREF))
    assert len(contacts) == 1
    existing_href = contacts[0]

    # GIVEN a contact href that doesn't exist in the database
    wrong_href = "nonexistent_href"
    assert wrong_href not in existing_href

    # WHEN attempting to update using the CLI
    new_href = "new.contact@mail.com"
    result = runner.invoke(
        cli,
        [
            "update",
            "contact",
            "--href",
            wrong_href,
            "--new-href",
            new_href,
            "--new-name",
            NEW_NAME,
            "--new-institution",
            TEST_INST,
        ],
        input="y",  # in case the CLI asks for confirmation
    )

    # THEN the CLI should succeed but print a message about no patients found
    assert result.exit_code == 0
    assert f"No patients found with query" in result.output

    # AND no patient contact should be updated
    updated_patient = patients_collection.find_one({CONTACT_HREF: f"mailto:{new_href}"})
    assert updated_patient is None


def test_update_contact_multiple_href_match(mock_app, gpx4_patients):
    """
    Test the command when the old contact href matches multiple patients.
    The CLI should print a warning and not update any patient contact.
    """

    runner = mock_app.test_cli_runner()
    patients_collection = mock_app.db.patients

    assert len(gpx4_patients) >= 2

    # GIVEN a database with 2 patients sharing similar href patterns
    gpx4_patients[0]["contact"]["href"] = "test_1@mail.com"
    gpx4_patients[1]["contact"]["href"] = "test_2@mail.com"
    patients_collection.insert_many(gpx4_patients)

    # WHEN attempting to update with a href pattern that matches multiple contacts
    old_href_pattern = "test_"  # this will match both test_1 and test_2
    new_href = "test_3@mail.com"

    result = runner.invoke(
        cli,
        [
            "update",
            "contact",
            "--href",
            old_href_pattern,
            "--new-href",
            new_href,
            "--new-name",
            NEW_NAME,
            "--new-institution",
            TEST_INST,
        ],
        input="y",
    )

    # THEN the CLI should print a warning about multiple matches
    assert result.exit_code == 0
    assert "returning more than one patients' contact" in result.output

    # AND no patient should be updated
    updated_patient = patients_collection.find_one({CONTACT_HREF: f"mailto:{new_href}"})
    assert updated_patient is None
