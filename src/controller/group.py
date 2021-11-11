from flask_socketio import emit, close_room

from errors import WeminderAPIError
from .user import get_user_session
import services as Services

parse_json = Services.parse_json

def on_create_group(args, user_id: str):
    try:
        group = Services.create_group(
            name=args['name'],
            alias=args['alias'],
            user_id=user_id
        )
        emit('on_create_group', parse_json(group), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_update_group(args):
    try:
        Services.update_group(args['_id'], args['name'], args['alias'])
        emit('on_update_group', parse_json(args), to=args['_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_join_group(args, user_id: str):
    try:
        group = Services.join_group(args['group_id'], user_id)
        users = Services.get_users([user_id])

        emit('on_join_group', parse_json(group), to=args['group_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_leave_group(args, user_id: str):
    try:
        last_user, group = Services.leave_group(args['group_id'], user_id)
        if last_user:
            close_room(args['group_id'])

        users = Services.get_users([user_id])
        emit('on_leave_group', parse_json(group), to=args['group_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_find_group(args, user_id: str):
    try:
        if (args.get('alias', None) is not None):
            group = Services.find_group_by_alias(args['alias'])

        if (args.get('group_id', None) is not None):
            group = Services.find_group_by_id(args['group_id'])

        emit('on_find_group', parse_json(group), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_find_user_groups(user_id: str):
    try:
        groups = Services.find_user_groups(user_id)
        emit('on_find_user_groups', parse_json(groups), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())


def on_find_group_users(args, user_id: str):
    try:
        user_ids = Services.find_group_users(args['group_id'])
        users = Services.get_users(user_ids)
        emit('on_find_group_users', parse_json(users), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())