import os

os.environ.setdefault("SQLALCHEMY_DATABASE_URI", 'sqlite:///:memory:')
import pytest
from application import app
from domain.base import Engine, Base, Session
from domain.entity.user import User
from domain.type.user_type import UserType
from datetime import datetime


@pytest.fixture(scope='session', autouse=True)
def create_test_database():
    Base.metadata.drop_all(bind=Engine)
    Base.metadata.create_all(bind=Engine)
    yield
    Base.metadata.drop_all(bind=Engine)


@pytest.fixture(autouse=True)
def transactional_test(create_test_database, request):
    connection = Engine.connect()
    transaction = connection.begin()

    try:
        nested = connection.begin_nested()

        Session.configure(bind=connection)
        yield

    finally:
        nested.rollback()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='module')
def test_client():
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


@pytest.fixture(scope='module')
def create_user():
    session = Session()
    test_user = User(
        role=UserType.ROOT_ADMIN,
        first_name="admin",
        last_name="admin",
        mobile_number="1234567890",
        email="admin",
        update_date_time=datetime.utcnow(),
        insert_date_time=datetime.utcnow(),
        password="$2a$12$BEOqNVY7cHlMztWNra87nuHAHqvex/ZgFfPmq5ZNNi4DxFHyflHau"
    )
    session.add(test_user)
    session.commit()
    user_id = test_user.id
    yield user_id
    session.delete(test_user)
    session.commit()
    session.close()


@pytest.fixture(scope='module')
def auth_token(test_client):
    login_payload = {
        "email": "admin",
        "password": "admin"
    }
    response = test_client.post('/authentication/login', json=login_payload)
    assert response.status_code == 200, "Failed to log in with the given credential"
    token = response.json['access_token']
    return token


# append jwt token to header of all the testing requests
@pytest.fixture(autouse=True)
def set_auth_header(test_client, auth_token):
    test_client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {auth_token}'
