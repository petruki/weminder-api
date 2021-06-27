import json

from bson import json_util

from .user import authenticate, signup, get_users
from .group import create_group, join_group, leave_group, find_group_by_alias, find_user_groups
from .task import create_task, list_tasks_by_group, update_task, delete_task, add_log

def parse_json(data):
    return json.loads(json_util.dumps(data))