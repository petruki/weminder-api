from flask_socketio import emit

from errors import WeminderAPIError
from .user import get_user_session
import services as Services

parse_json = Services.parse_json

def on_create_task(args, user_id: str):
    try:
        task = Services.create_task(
            user_id=user_id,
            group_id=args.get('group_id', None),
            title=args.get('title', None),
            content=args.get('content', None),
            status=args.get('status', None)
        )
        emit('on_create_task', parse_json(task), to=args['group_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_get_task(args, user_id: str):
    try:
        task = Services.get_task(args.get('task_id', None))
        emit('on_get_task', parse_json(task), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_list_tasks(args, user_id: str):
    try:
        tasks = Services.list_tasks_by_group(args['group_id'])
        emit('on_list_tasks', parse_json(tasks), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_update_task(args, user_id: str):
    try:
        user = Services.get_user_by_id(user_id)
        current_task = Services.get_task(args.get('_id', None))
        task = Services.update_task(
            current_task=current_task,
            task_id=args.get('_id', None),
            title=args.get('title', None),
            content=args.get('content', None),
            status=args.get('status', None),
            username=user['username']
        )

        if task is not None:
            emit('on_update_task', parse_json(task), to=args['group_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_add_log(args, user_id: str):
    try:
        user = Services.get_user_by_id(user_id)
        task = Services.add_log(
            task_id=args.get('task_id', None),
            content=args.get('content', None),
            username=user['username']
        )

        if task is not None:
            emit('on_update_task', parse_json(task), to=args['group_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_delete_task(args):
    try:
        if Services.delete_task(args.get('_id', None)):
            emit('on_delete_task', { 
                'message': 'Task deleted',
                'task_id': args['_id']
            }, to=args['group_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())