from app.main import app
from unittest.mock import patch, Mock, call
from app.models.entities.Specialty import Specialty

new_value = 4000
specialty_dictionary = {"id": "an_id", "name": "a_name", "value": 3500}
specialty = Specialty(**specialty_dictionary)


@patch("app.models.entities.Specialty.db.collection")
def test_updates_self_value(mock_db_connection):
    updated_specialty = specialty.update_value(new_value)
    assert updated_specialty.value == new_value


@patch("app.models.entities.Specialty.db.collection")
def test_db_connection(mock_db_connection):
    specialty.update_value(new_value)

    assert mock_db_connection.call_count == 2

    mock_db_connection.assert_has_calls(
        [
            call("specialties"),
            call().document(specialty_dictionary["id"]),
            call().document().update({"value": new_value}),
            call("physicians"),
            call().where("appointment_value", ">", new_value * 2),
            call().where().get(),
        ]
    )
