import pytest as pytest

from domain.base import Session, Engine
from services.optimiser.input_processing import *

# Todo: Mock session

@pytest.fixture
def session():
    new_session = Session(bind=Engine)
    yield new_session

    new_session.close()


@pytest.fixture
def request_id():
    return '356'


def test_get_input_qualrequirements(session, request_id):
    print(get_input_qualrequirements(session, request_id))


def test_get_input_rolerequirements(session, request_id):
    print(get_input_rolerequirements(session, request_id))


def test_get_input_posrequirements(session, request_id):
    print(get_input_posrequirements(session, request_id))


def test_get_input_qualability(session):
    print(get_input_qualability(session))


def test_get_input_roleability(session):
    print(get_input_roleability(session))


def test_get_input_availability(session, request_id):
    print(get_input_availability(session, request_id))


