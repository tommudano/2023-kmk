import pytest
from fastapi import HTTPException
from app.main import app
from app.models.entities.Physician import Physician
from app.models.entities.Specialty import Specialty
from unittest.mock import patch, Mock

physician = Physician(
    **{
        "role": "physician",
        "first_name": "test",
        "last_name": "test",
        "tuition": "A123456",
        "specialty": "cardiologia",
        "email": "test@email.com",
        "id": "123456789",
        "approved": "approved",
        "agenda": {"1": {"start": 8, "finish": 18.5}},
        "appointment_value": 4000,
    }
)

specialty = Specialty(**{"id": "123456", "name": "a_name", "value": 5000})


@patch("app.models.entities.Physician.db.collection")
@patch("app.models.entities.Physician.Specialty.get_by_name")
def test_update_value_function_queries_db(mock_specialty, mock_db_query):
    new_value = 4500
    mock_specialty.return_value = specialty
    physician.update_appointment_value(new_value)
    mock_db_query.assert_called_with("physicians")
    mock_db_query().document.assert_called_with(physician.id)
    mock_db_query().document().update.assert_called_with(
        {"appointment_value": new_value}
    )


@patch("app.models.entities.Physician.db.collection")
@patch("app.models.entities.Physician.Specialty.get_by_name")
def test_update_value_function_gets_specialty(mock_specialty, mock_db_query):
    new_value = 4500
    mock_specialty.return_value = specialty
    physician.update_appointment_value(new_value)
    mock_specialty.assert_called_with(physician.specialty)


@patch("app.models.entities.Physician.db.collection")
@patch("app.models.entities.Physician.Specialty.get_by_name")
def test_update_value_function_returns_an_updated_instance_of_Physician(
    mock_specialty, mock_db_query
):
    new_value = 4500
    mock_specialty.return_value = specialty
    new_physician_instance = physician.update_appointment_value(new_value)
    assert type(new_physician_instance) == Physician
    assert new_physician_instance.__dict__ == {
        **physician.__dict__,
        "appointment_value": new_value,
    }


@patch("app.models.entities.Physician.db.collection")
@patch("app.models.entities.Physician.Specialty.get_by_name")
def test_update_with_more_than_the_double_throws_http_exception(
    mock_specialty, mock_db_query
):
    new_value = specialty.value * 2 + 1
    mock_specialty.return_value = specialty
    with pytest.raises(HTTPException) as http_exception:
        physician.update_appointment_value(new_value)

    assert http_exception.value.status_code == 400
    assert (
        http_exception.value.detail
        == "El nuevo valor debe ser menor o igual al doble del valo que uso el administrador"
    )
