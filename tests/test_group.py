import pytest
import bson

from bson.objectid import ObjectId

from src.app import socketio
from src.services.group import find_group_by_alias

from tests.util import logged_as, get_args
from tests.fixtures.user_fixtures import setup_db_user, tear_down_user
from tests.fixtures.group_fixtures import tear_down_group

@pytest.fixture(scope='module', autouse=True)
def setup_fixture():
    setup_db_user()
    yield
    tear_down_user()
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
    assert get_args(res)['name'] == 'Project 1'
    assert get_args(res)['alias'] == 'pj1'
    assert len(get_args(res)['users']) > 0

@logged_as('roger', '123')
def test_on_create_group_fail(socketio_test_client):
    socketio_test_client.emit('create_group', {
        'name': 'Project 1',
        'alias': ''
    })

    res = socketio_test_client.get_received()
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == 'Alias cannot be empty'
    assert get_args(res)['status'] == 400

@logged_as('anna', '123')
def test_on_find_group(socketio_test_client):
    socketio_test_client.emit('find_group', {
        'alias': 'pj1'
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_find_group'
    assert get_args(res)['name'] == 'Project 1'
    assert get_args(res)['alias'] == 'pj1'
    assert bson.objectid.ObjectId.is_valid(get_args(res)['_id']['$oid'])

@logged_as('anna', '123')
def test_on_find_group_fail(socketio_test_client):
    socketio_test_client.emit('find_group', {
        'alias': 'NOT_FOUND'
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == 'NOT_FOUND not found'
    assert get_args(res)['status'] == 404

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
    assert get_args(res)['user'] == 'anna'

    group = find_group_by_alias('pj1')
    assert len(group['users']) == 2

@logged_as('anna', '123')
def test_on_join_group_fail(socketio_test_client):
    socketio_test_client.emit('join_group', {
        'group_id': ObjectId().__str__()
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['status'] == 500

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
    assert get_args(res)['user'] == 'anna'

    group = find_group_by_alias('pj1')
    assert len(group['users']) == 1

@logged_as('anna', '123')
def test_on_leave_group_fail(socketio_test_client):
    socketio_test_client.emit('leave_group', {
        'group_id': ObjectId().__str__()
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['status'] == 500

@logged_as('roger', '123')
def test_on_find_user_group(socketio_test_client):
    socketio_test_client.emit('find_user_groups', {})

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_find_user_groups'
    assert len(get_args(res)) == 1