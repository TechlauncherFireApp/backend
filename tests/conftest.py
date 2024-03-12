import os

os.environ.setdefault('username', 'user')
os.environ.setdefault('password', 'password')
os.environ.setdefault('host', '127.0.0.1')
os.environ.setdefault('port', '3306')
os.environ.setdefault('dbname', 'db')
from application import create_app
import pytest


@pytest.fixture(scope='module')
def test_client():
    # Set the Testing configuration prior to creating the Flask application
    flask_app = create_app()

    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client


@pytest.fixture(scope='module')
def auth_token(test_client):
    # Login with predefined admin credentials
    login_payload = {  # admin account details
        'email': 'admin',
        'password': 'admin'
    }
    response = test_client.post('/authentication/login', json=login_payload)
    assert response.status_code == 200, "Failed to log in with the given credential"
    print(response.json)
    token = response.json['access_token']
    return token

# append jwt token to header of all the testing requests
@pytest.fixture(autouse=True)
def set_auth_header(test_client, auth_token):
    test_client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {auth_token}'
