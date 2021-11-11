import pytest
import json
from bson.objectid import ObjectId

from src.app import socketio
from src.services.group import find_group_by_alias
from src.services.task import list_tasks_by_group

from tests.util import logged_as, get_args
from tests.fixtures.user_fixtures import setup_db_user, tear_down_user
from tests.fixtures.task_fixtures import tear_down_task
from tests.fixtures.group_fixtures import (
    setup_db_group, 
    tear_down_group, 
    add_user_to_group
)

@pytest.fixture(scope='module', autouse=True)
def setup_fixture():
    setup_db_user()
    setup_db_group()
    yield
    tear_down_user()
    tear_down_group()
    tear_down_task()

@logged_as('roger', '123')
def test_on_create_task(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    add_user_to_group(group['_id'], 'roger')

    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('create_task', json.dumps({
        'group_id': str(group['_id']),
        'title': 'Task 1',
        'content': 'Write some unit tests',
        'status': 'TODO'
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_create_task'
    assert get_args(res)['title'] == 'Task 1'
    assert get_args(res)['status'] == 'TODO'
    assert len(get_args(res)['log']) == 0

@logged_as('roger', '123')
def test_on_get_task(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    tasks = list_tasks_by_group(str(group['_id']))

    # test
    socketio_test_client.emit('get_task', json.dumps({
        'group_id': str(group['_id']),
        'task_id': str(tasks[0]['_id'])
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_get_task'
    assert get_args(res)['title'] == 'Task 1'
    assert get_args(res)['status'] == 'TODO'
    assert len(get_args(res)['log']) == 0

@logged_as('roger', '123')
def test_on_get_task_not_found(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')

    # test
    task_id = ObjectId().__str__()
    socketio_test_client.emit('get_task', json.dumps({
        'group_id': str(group['_id']),
        'task_id': task_id
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == f'{task_id.__str__()} not found'

@logged_as('roger', '123')
def test_on_create_task_fail(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')

    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('create_task', json.dumps({
        'group_id': str(group['_id']),
        'title': 'Task 2',
        'content': 'Status is not valid',
        'status': ''
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == 'Status cannot be empty'
    assert get_args(res)['status'] == 400

@logged_as('roger', '123')
def test_on_list_tasks(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('list_tasks', json.dumps({
        'group_id': str(group['_id'])
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_list_tasks'
    assert str(get_args(res)[0]['group_id']) == str(group['_id'])
    assert get_args(res)[0]['title'] == 'Task 1'
    assert get_args(res)[0]['created_by']['username'] == 'roger'

@logged_as('roger', '123')
def test_on_list_tasks_fail(socketio_test_client):
    socketio_test_client.emit('list_tasks', json.dumps({
        'group_id': ''
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == 'Group ID cannot be empty'
    assert get_args(res)['status'] == 400

@logged_as('roger', '123')
def test_on_update_task(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    tasks = list_tasks_by_group(str(group['_id']))

    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('update_task', json.dumps({
        'group_id': str(group['_id']),
        'task_id': str(tasks[0]['_id']),
        'content': 'Updated content'
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_update_task'
    assert get_args(res)['content'] == 'Updated content'
    assert len(get_args(res)['log']) == 1

@logged_as('roger', '123')
def test_on_update_task_fail(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    tasks = list_tasks_by_group(str(group['_id']))

    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('update_task', json.dumps({
        'group_id': str(group['_id']),
        'task_id': str(tasks[0]['_id']),
        'content': ''
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == 'Content cannot be empty'
    assert get_args(res)['status'] == 400

@logged_as('roger', '123')
def test_on_add_task_log(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    tasks = list_tasks_by_group(str(group['_id']))

    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('add_log', json.dumps({
        'group_id': str(group['_id']),
        'task_id': str(tasks[0]['_id']),
        'content': 'New log item'
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_update_task'
    assert len(get_args(res)['log']) == 2
    assert get_args(res)['log'][1]['message'] == 'New log item'

@logged_as('roger', '123')
def test_on_add_task_log_fail(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    tasks = list_tasks_by_group(str(group['_id']))

    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('add_log', json.dumps({
        'group_id': str(group['_id']),
        'task_id': str(tasks[0]['_id']),
        'content': ''
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == 'Content cannot be empty'
    assert get_args(res)['status'] == 400

@logged_as('roger', '123')
def test_on_delete_task(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    tasks = list_tasks_by_group(str(group['_id']))

    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('delete_task', json.dumps({
        'group_id': str(group['_id']),
        'task_id': str(tasks[0]['_id'])
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_delete_task'
    assert get_args(res)['task_id'] == str(tasks[0]['_id'])
    assert get_args(res)['message'] == 'Task deleted'

@logged_as('roger', '123')
def test_on_delete_task_fail(socketio_test_client):
    # given
    group = find_group_by_alias('FIXTURE1')
    
    socketio_test_client.emit('join_room', json.dumps({ 'group_id': str(group['_id']) }))
    socketio_test_client.get_received()

    # test
    socketio_test_client.emit('delete_task', json.dumps({
        'group_id': str(group['_id']),
        'task_id': 'INVALID_ID'
    }))

    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_error'
    assert get_args(res)['error'] == 'Invalid Task ID'
    assert get_args(res)['status'] == 400