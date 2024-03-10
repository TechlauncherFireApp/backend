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
    print("hello")

    # Set the Testing configuration prior to creating the Flask application
    flask_app = create_app()

    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client


