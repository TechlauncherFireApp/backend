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


# Todo: using the mock database to test.

#  Input: The database and the vehicle id.
#  Expected output: A matrix of (A, P, Q). Indicates the qualifications for the vehicle on all shifts.
#  A-The number of shifts for this vehicle attend. P-The number of position. Q-The number of qualifications.
def test_get_input_qualrequirements(session, request_id):
    print(get_input_qualrequirements(session, request_id))


#  Input: The database and the vehicle id.
#  Expected output: A matrix of (A, P, R). Indicates the roles for the vehicle on all shifts.
#  A-The number of shifts for this vehicle attend. P-The number of position. R-The number of roles.
def test_get_input_rolerequirements(session, request_id):
    print(get_input_rolerequirements(session, request_id))


#  Input: The database and the vehicle id.
#  Expected output: A matrix of (P, A). Indicates the number of positions of the vehicle on all shifts.
#  P-The number of position. A-The number of shifts for this vehicle attend.
def test_get_input_posrequirements(session, request_id):
    print(get_input_posrequirements(session, request_id))


#  Input: The database and the vehicle id.
#  Expected output: A matrix of (V, Q). Indicates the qualifications for all volunteers.
#  V-The number of volunteers. Q-The number of qualifications.
def test_get_input_qualability(session):
    print(get_input_qualability(session))


#  Input: The database and the vehicle id.
#  Expected output: A matrix of (V, R). Indicates the roles for all volunteers.
#  V-The number of volunteers. R-The number of roles.
def test_get_input_roleability(session):
    print(get_input_roleability(session))


#  Input: The database and the vehicle id.
#  Expected output: A matrix of (V, A). Indicates the volunteer's availability during the scheduled shift time.
#  V-The number of volunteers. A-The number of shifts for this vehicle attend.
def test_get_input_availability(session, request_id):
    print(get_input_availability(session, request_id))


