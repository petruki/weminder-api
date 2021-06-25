import pytest

from tests.util import logged_as
from tests.fixtures.user_fixtures import setup_db_user, tear_down_user

@pytest.fixture(scope='module', autouse=True)
def setup_fixture():
    setup_db_user()
    yield
    tear_down_user()

@logged_as('roger', '123')
def test_on_check(socketio_test_client):
    socketio_test_client.emit('check', {
        'user': 'roger'
    })
    
    res = socketio_test_client.get_received()
    assert len(res[0]['args']) == 1
    assert res[0]['name'] == 'on_check'
    assert res[0]['args'][0]['message'] == 'All good roger'