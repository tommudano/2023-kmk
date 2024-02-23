import pytest
from unittest.mock import patch, Mock
from app.main import app
from app.models.entities.Physician import Physician


physician = {
    "role": "physician",
    "first_name": "test",
    "last_name": "test",
    "tuition": "A123456",
    "specialty": "cardiologia",
    "email": "test@email.com",
    "id": "123456789",
    "approved": "approved",
    "agenda": {"1": {"start": 8, "finish": 18.5}},
    "appointment_value": 1000,
}


@patch("app.models.entities.Physician.db.collection")
def test_function_queries_db(mock_db):
    id = physician["id"]
    mock_response = Mock()
    mock_response.document().get().to_dict.return_value = physician
    mock_db.return_value = mock_response

    Physician.get_by_id(id)
    mock_db.assert_called_with("physicians")
    mock_db().document.assert_called_with(id)
    mock_db().document().get.assert_called_with()


@patch("app.models.entities.Physician.db.collection")
def test_function_returns_a_physician_instance(mock_db):
    id = physician["id"]
    mock_response = Mock()
    mock_response.document().get().to_dict.return_value = physician
    mock_db.return_value = mock_response

    returned_physician = Physician.get_by_id(id)
    assert type(returned_physician) == Physician
    assert returned_physician.__dict__ == Physician(**physician).__dict__
