import json

from bson import json_util

from .user import authenticate, signup, get_users, get_user_by_id
from .group import create_group, update_group, join_group, leave_group, find_group_by_alias, find_user_groups, find_group_users, find_group_by_id
from .task import create_task, get_task, list_tasks_by_group, update_task, delete_task, add_log

def parse_json(data):
    return json.loads(json_util.dumps(data))