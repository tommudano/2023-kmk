import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from app.main import app
from app.models.entities.Physician import Physician
from app.models.entities.Specialty import Specialty

today_date = datetime.fromtimestamp(round(time.time()))
number_of_day_of_week = today_date.date().strftime("%w")
next_week_day = today_date + timedelta(days=7)
next_week_day_off_by_one_day = today_date + timedelta(days=8)
next_week_day_first_block = next_week_day.replace(hour=9)
next_week_day_second_block = next_week_day.replace(hour=10)
next_week_day_off_by_hours = next_week_day.replace(hour=21)
another_next_week_day_off_by_hours = next_week_day.replace(hour=3)

physician = Physician(
    **{
        "role": "physician",
        "first_name": "test",
        "last_name": "test",
        "tuition": "A123456",
        "specialty": "cardiologia",
        "email": "test@email.com",
        "id": "123456789",
        "approved": "blocked",
        "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
        "appointments": {str(round(next_week_day_first_block.timestamp())): True},
        "appointment_value": 1000,
    }
)


def test_available_date_returns_true():
    assert physician.has_availability(round(next_week_day_second_block.timestamp()))


def test_non_available_date_returns_false():
    assert not physician.has_availability(round(next_week_day_first_block.timestamp()))


def test_date_after_working_hours_returns_false():
    assert not physician.has_availability(round(next_week_day_off_by_hours.timestamp()))


def test_date_before_working_hours_returns_false():
    assert not physician.has_availability(
        round(another_next_week_day_off_by_hours.timestamp())
    )


def test_date_in_non_working_days_returns_false():
    assert not physician.has_availability(
        round(next_week_day_off_by_one_day.timestamp())
    )
