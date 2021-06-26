import pytest
import json

from src.app import app, socketio

@pytest.fixture
def rest_client():
    with app.test_client() as flask_test_client:
        yield flask_test_client

def logged_as(username: str = None, password: str = None, consume: bool = True):
    def with_logging(func):
        def wrapper(*args, **kwargs):
            flask_test_client = app.test_client()
            flask_test_client.post('/login', data = { 'username': username, 'password': password })
            socketio_test_client = socketio.test_client(
                app, flask_test_client = flask_test_client)

            if socketio_test_client.is_connected() and consume:
                socketio_test_client.get_received()

            return func(socketio_test_client)
        return wrapper
    return with_logging

def load_res(res) -> dict:
    return json.loads(res.data.decode('utf8'))

def get_args(res):
    return res[0]['args'][0]