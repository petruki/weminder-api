import pytest

from src.services.group import find_group_by_alias
from src.services.task import create_task, list_tasks_by_group, update_task

from tests.fixtures.user_fixtures import setup_db_user, tear_down_user
from tests.fixtures.task_fixtures import tear_down_task
from tests.fixtures.group_fixtures import (
    setup_db_group, 
    tear_down_group, 
    add_user_to_group
)

@pytest.fixture(scope='module', autouse=True)
def setup_fixture():
    users = setup_db_user()
    setup_db_group()
    yield users
    tear_down_user()
    tear_down_group()
    tear_down_task()

def test_list_tasks(setup_fixture):
    # given
    roger = setup_fixture[0]
    group = find_group_by_alias('FIXTURE1')
    add_user_to_group(group['_id'], roger['username'])

    create_task(
        user_id=str(roger['_id']), 
        group_id=str(group['_id']), 
        title='New Task', 
        content='Task content', 
        status='TODO'
    )

    # test
    tasks = list_tasks_by_group(str(group['_id']))
    assert len(tasks) == 1
    assert tasks[0]['title'] == 'New Task'
    assert tasks[0]['created_by']['username'] == roger['username']

def test_update_task(setup_fixture):
    # given
    group = find_group_by_alias('FIXTURE1')
    tasks = list_tasks_by_group(str(group['_id']))

    # test
    task = update_task(
        task_id=str(tasks[0]['_id']),
        title='New Title'
    )

    assert task['status'] == 'TODO'
    assert task['title'] == 'New Title'

    task = update_task(
        task_id=str(tasks[0]['_id']),
        status='DOING'
    )

    assert task['status'] == 'DOING'
    assert len(task['log']) == 2