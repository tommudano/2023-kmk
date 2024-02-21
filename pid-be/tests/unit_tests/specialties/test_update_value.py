from app.main import app
from unittest.mock import patch, Mock
from app.models.entities.Specialty import Specialty

newValue = 4000
specialty_dictionary = {"id": "an_id", "name": "a_name", "value": 3500}
specialty = Specialty(**specialty_dictionary)


@patch("app.models.entities.Specialty.db.collection")
def test_updates_self_value(mock_db_connection):
    updated_specialty = specialty.update_value(newValue)
    assert updated_specialty.value == newValue


@patch("app.models.entities.Specialty.db.collection")
def test_db_connection(mock_db_connection):
    specialty.update_value(newValue)
    mock_db_connection.assert_called_with("specialties")
    mock_db_connection().document.assert_called_with(specialty_dictionary["id"])
    mock_db_connection().document().update.assert_called_with({"value": newValue})
