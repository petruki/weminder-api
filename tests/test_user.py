import pytest
import json

from src.app import socketio

from tests.util import rest_client, logged_as, load_res, get_args
from tests.fixtures.user_fixtures import setup_db_user, tear_down_user

@pytest.fixture(scope='module', autouse=True)
def setup_fixture():
    setup_db_user()
    yield
    tear_down_user()

@logged_as('roger', 'invalid_password', consume = False)
def test_not_logged(socketio_test_client):
    assert not socketio_test_client.is_connected()

@logged_as('roger', '123', consume = False)
def test_logged(socketio_test_client):
    assert socketio_test_client.is_connected()

    res = socketio_test_client.get_received()
    assert len(res) == 1
    assert res[0]['name'] == 'connected'
    assert len(res[0]['args']) == 1
    assert len(get_args(res)['id']) > 0

def test_signup(rest_client):
    res = rest_client.post('/signup', 
        data=json.dumps(dict(
            username='new_user', 
            password='new_user_passsword'
        )), content_type='application/json')
        
    body = load_res(res)
    
    assert res.status_code == 201
    assert body['username'] == 'new_user'

def test_signup_fail_password(rest_client):
    res = rest_client.post('/signup', 
        data=json.dumps(dict(
            username='small_password', 
            password='1'
        )), content_type='application/json')

    body = load_res(res)

    assert res.status_code == 400
    assert body['error'] == 'Password cannot be less than 2 characters'

def test_signup_fail_no_username(rest_client):
    res = rest_client.post('/signup',
        data=json.dumps(dict(
            username='', 
            password='new_user_passsword'
        )), content_type='application/json')

    body = load_res(res)

    assert res.status_code == 400
    assert body['error'] == 'Username cannot be empty'

@logged_as('new_user', 'new_user_passsword', consume=False)
def test_logged_new_user(socketio_test_client):
    assert socketio_test_client.is_connected()

    res = socketio_test_client.get_received()
    assert len(res) == 1
    assert res[0]['name'] == 'connected'
    assert len(res[0]['args']) == 1
    assert len(get_args(res)['id']) > 0

def test_on_me(rest_client):
    # given
    rest_client.post('/login',
        data=json.dumps(dict(
            username='new_user', 
            password='new_user_passsword'
        )), content_type='application/json')

    # test
    res = rest_client.get('/me')
    body = load_res(res)

    assert res.status_code == 200
    assert body['username'] == 'new_user'

def test_on_me_fail_not_logged(rest_client):
    res = rest_client.get('/me')
    assert res.status_code == 401

def test_logout(rest_client):
    # given
    rest_client.post('/login',
        data=json.dumps(dict(
            username='new_user', 
            password='new_user_passsword'
        )), content_type='application/json')

    # test
    res = rest_client.post('/logout')
    assert res.status_code == 200