import pytest
from unittest.mock import patch, Mock
from app.main import app
from app.models.entities.Physician import Physician


class Test_physician_db_object:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return {
            "role": "physician",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "tuition": "A123456",
            "specialty": "cardiologia",
            "email": "test@email.com",
            "id": "123456789",
            "approved": "approved",
            "agenda": {"1": {"start": 8, "finish": 18.5}},
            "appointment_value": 1000,
        }


@patch("app.models.entities.Physician.db.collection")
def test_function_calls_db(mock_get):
    specialty_name = "cardiologia"
    mock_response = Mock()
    response = [Test_physician_db_object("test", "test")]

    mock_response.where().where().get.return_value = response
    mock_get.return_value = mock_response

    Physician.get_approved_by_specialty(specialty_name)
    mock_get.assert_called_with("physicians")
    mock_get().where.assert_called_with("specialty", "==", specialty_name)
    mock_get().where().where.assert_called_with("approved", "==", "approved")
    mock_get().where().where().get.assert_called_with()


@patch("app.models.entities.Physician.db.collection")
def test_function_returns_list_of_physicians(mock_get):
    test_physician_obj = Test_physician_db_object("test", "test")
    mock_response = Mock()
    response = [test_physician_obj]

    mock_response.where().where().get.return_value = response
    mock_get.return_value = mock_response

    physicians_list = Physician.get_approved_by_specialty("cardiologia")
    assert type(physicians_list) == list
    assert len(physicians_list) == 1
    assert type(physicians_list[0]) == dict
    assert physicians_list[0] == Physician(**test_physician_obj.to_dict()).__dict__


@patch("app.models.entities.Physician.db.collection")
def test_function_returns_sorted_by_full_name_list_of_physicians(mock_get):
    first_test_physician_obj = Test_physician_db_object("Test", "Test")
    second_test_physician_obj = Test_physician_db_object("test", "test")
    third_test_physician_obj = Test_physician_db_object("a name", "test")
    fourth_test_physician_obj = Test_physician_db_object("test", "A last name")
    mock_response = Mock()
    response = [
        first_test_physician_obj,
        second_test_physician_obj,
        third_test_physician_obj,
        fourth_test_physician_obj,
    ]

    mock_response.where().where().get.return_value = response
    mock_get.return_value = mock_response

    physicians_list = Physician.get_approved_by_specialty("cardiologia")
    assert len(physicians_list) == 4
    assert (
        physicians_list[0] == Physician(**third_test_physician_obj.to_dict()).__dict__
    )
    assert (
        physicians_list[1] == Physician(**fourth_test_physician_obj.to_dict()).__dict__
    )
    assert (
        physicians_list[2] == Physician(**first_test_physician_obj.to_dict()).__dict__
    )
    assert (
        physicians_list[3] == Physician(**second_test_physician_obj.to_dict()).__dict__
    )
