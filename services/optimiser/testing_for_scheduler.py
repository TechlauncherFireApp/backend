import pytest
from domain.base import Session, Engine
from services.optimiser.input_processing import (
    get_input_clashes,
    get_vehicle_time,
    get_vehicle_list,
    get_position_list,
    get_position_list_all,

)


@pytest.fixture
def session():
    new_session = Session(bind=Engine)
    yield new_session

    new_session.close()


@pytest.fixture
def request_id():
    return '322'

@pytest.fixture
def vehicle_id():
    return  '369'



def test_get_input_clashes(session,request_id):
    print(get_input_clashes(session,request_id))
def test_get_vehicle_time(session,vehicle_id):
    print(get_vehicle_time(session,vehicle_id))
def test_get_vehicle_list(session,request_id):
    print(get_vehicle_list(session,request_id))

def test_get_position_list(session,vehicle_id):
    print(get_position_list(session,vehicle_id))

def test_get_position_list_all(session,request_id):
    print(get_position_list_all(session,request_id))







