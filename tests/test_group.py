import pytest
import bson

from src.app import socketio
from src.services.group import find_group_by_alias

from tests.util import logged_as
from tests.fixtures.auth_fixtures import setup_db_auth, tear_down_auth
from tests.fixtures.group_fixtures import tear_down_group

@pytest.fixture(scope='module', autouse=True)
def setup_fixture():
    setup_db_auth()
    yield
    tear_down_auth()
    tear_down_group()

@logged_as('roger', '123')
def test_on_create_group(socketio_test_client):
    socketio_test_client.emit('create_group', {
        'name': 'Project 1',
        'alias': 'pj1'
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_create_group'
    assert res[0]['args'][0]['name'] == 'Project 1'
    assert res[0]['args'][0]['alias'] == 'pj1'
    assert len(res[0]['args'][0]['users']) > 0

@logged_as('anna', '123')
def test_on_find_group(socketio_test_client):
    socketio_test_client.emit('find_group', {
        'alias': 'pj1'
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_find_group'
    assert res[0]['args'][0]['name'] == 'Project 1'
    assert res[0]['args'][0]['alias'] == 'pj1'
    assert bson.objectid.ObjectId.is_valid(res[0]['args'][0]['_id']['$oid']) 

@logged_as('anna', '123')
def test_on_join_group(socketio_test_client):
    # given
    group = find_group_by_alias('pj1')
    assert group is not None

    # test
    socketio_test_client.emit('join_group', {
        'group_id': str(group['_id'])
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_join_group'
    assert res[0]['args'][0]['status'] == 200

    group = find_group_by_alias('pj1')
    assert len(group['users']) == 2

@logged_as('anna', '123')
def test_on_leave_group(socketio_test_client):
    # given
    group = find_group_by_alias('pj1')
    assert group is not None
    assert len(group['users']) == 2

    socketio_test_client.emit('join_room', { 'group_id': str(group['_id']) })
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('leave_group', {
        'group_id': str(group['_id'])
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_leave_group'
    assert res[0]['args'][0]['status'] == 200

    group = find_group_by_alias('pj1')
    assert len(group['users']) == 1

@logged_as('roger', '123')
def test_on_find_user_group(socketio_test_client):
    socketio_test_client.emit('find_user_groups', {})

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_find_user_groups'
    assert len(res[0]['args'][0]) == 1