import pytest
import json

from src.app import app, socketio

@pytest.fixture
def rest_client():
    with app.test_client() as flask_test_client:
        yield flask_test_client

def logged_as(username: str = None, password: str = None, consume: bool = True, channel = ""):
    def with_logging(func):
        def wrapper(*args, **kwargs):
            flask_test_client = app.test_client()
            res = flask_test_client.post('/login', 
                data=json.dumps(dict(username=username, password=password)), content_type='application/json')
                
            if res.status_code == 200:
                user_id = load_res(res)['_id']
                socketio_test_client = socketio.test_client(app, query_string=f'auth={user_id}&channel={channel}')
                if socketio_test_client.is_connected() and consume:
                    socketio_test_client.get_received()

                return func(socketio_test_client)
        return wrapper
    return with_logging

def load_res(res) -> dict:
    return json.loads(res.data.decode('utf8'))

def get_args(res):
    return res[0]['args'][0]