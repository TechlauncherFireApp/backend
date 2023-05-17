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

#  Input:  The database and the request id.
#  Output: A 2-dimensional matrix of size [A, A] that contains boolean values.
#  A- represent whether each asset shift clashes  with other asset shifts
def test_get_input_clashes(session,request_id):
    print(get_input_clashes(session,request_id))

#  Input: The database and the vehicle id.
#  Output: A 6-dimensional matrix of size [year,Month,Day,Hour,Minute,Second] means the time of vehicle .
def test_get_vehicle_time(session,vehicle_id):
    print(get_vehicle_time(session,vehicle_id))

#  Input:  The database and the request id.
#  Output: A 2-dimensional matrix of size [vehicle_id, vehicle_id] that contains vehicle_id that request_id order.
#  output: The dimensionality of the output matrix depends on how many vehicles are required for this request id
#  Tips:   This data is stored in table[asset_request_vehicle] and the "id" filed represent the vehicle_id
def test_get_vehicle_list(session,request_id):
    print(get_vehicle_list(session,request_id))

#  Input:  The database and the vehicle id.
#  Output: A 3-dimensional matrix of size [position id,position id,position id]
#  output: The dimensionality of the output matrix depends on how many position are related to this vehicle id
def test_get_position_list(session,vehicle_id):
    print(get_position_list(session,vehicle_id))

#  Input:  The database and the vehicle id.
#  Output: A 3-dimensional matrix of size [position id,position id,position id].
#  This matrix will be sorted based on the size of the numbers
def test_get_position_list_all(session,request_id):
    print(get_position_list_all(session,request_id))







