from app.main import app
from app.models.entities.Specialty import Specialty
from unittest.mock import patch, Mock


class MockSpecialty:
    def to_dict(self):
        return {"id": "an_id", "name": "A_name", "value": 3500}


@patch("app.models.entities.Specialty.db.collection")
def test_connection_to_firestore(mocked_db_query):
    mocked_specialty = MockSpecialty()
    name = mocked_specialty.to_dict()["name"]
    mock_response = Mock()
    mock_response.where().get.return_value = [mocked_specialty]
    mocked_db_query.return_value = mock_response

    Specialty.get_by_name(name)
    mocked_db_query.assert_called_with("specialties")
    mocked_db_query().where.assert_called_with("name", "==", name.lower())
    mocked_db_query().where().get.assert_called_with()


@patch("app.models.entities.Specialty.db.collection")
def test_method_returns_a_specialty(mocked_db_query):
    mocked_specialty = MockSpecialty()
    name = mocked_specialty.to_dict()["name"]
    mock_response = Mock()
    mock_response.where().get.return_value = [mocked_specialty]
    mocked_db_query.return_value = mock_response

    returned_specialty = Specialty.get_by_name(name)
    assert type(returned_specialty) == Specialty
    assert returned_specialty.__dict__ == {
        **mocked_specialty.to_dict(),
        "name": name.lower(),
    }
