from flask_socketio import emit

from errors import WeminderAPIError
from .user import get_user_session
import services as Services

parse_json = Services.parse_json

def on_create_task(args, user_id: str):
    try:
        task = Services.create_task(
            user_id=user_id,
            group_id=args['group_id'],
            title=args['title'],
            content=args['content'],
            priority=args['priority']
        )
        emit('on_create_task', parse_json(task), to=args['group_id'])
    except WeminderAPIError as e:
        emit('error', e.json())

def on_list_tasks(args, user_id: str):
    try:
        tasks = Services.list_tasks_by_group(args['group_id'])
        emit('on_list_tasks', parse_json(tasks), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('error', e.json())