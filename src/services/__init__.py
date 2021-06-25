import json

from bson import json_util

from .user import authenticate, signup
from .group import create_group, join_group, leave_group, find_group_by_alias, find_user_groups
from .task import create_task

def parse_json(data):
    return json.loads(json_util.dumps(data))