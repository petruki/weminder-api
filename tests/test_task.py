import pytest
import bson

from src.app import socketio
from src.services.group import find_group_by_alias

from tests.util import logged_as
from tests.fixtures.auth_fixtures import setup_db_auth, tear_down_auth
from tests.fixtures.task_fixtures import tear_down_task
from tests.fixtures.group_fixtures import (
    setup_db_group, 
    tear_down_group, 
    add_user_to_group
)

@pytest.fixture(scope='module', autouse=True)
def setup_fixture():
    setup_db_auth()
    setup_db_group()
    yield
    tear_down_auth()
    tear_down_group()
    tear_down_task()

@logged_as('roger', '123')
def test_on_create_task(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    add_user_to_group(group['_id'], 'roger')

    socketio_test_client.emit('join_room', { 'group_id': str(group['_id']) })
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('create_task', {
        'group_id': str(group['_id']),
        'title': 'Task 1',
        'content': 'Write some unit tests',
        'priority': 1
    })

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_create_task'
    assert res[0]['args'][0]['title'] == 'Task 1'
    assert res[0]['args'][0]['priority'] == 1