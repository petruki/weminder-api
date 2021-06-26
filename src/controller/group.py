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

def on_join_group(args, user_id: str):
    try:
        Services.join_group(args['group_id'], user_id)
        users = Services.get_users([user_id])

        emit('on_join_group', { 
            'message': f" User {users[0]['username']} has joined",
            'user': users[0]['username']
        })
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_leave_group(args, user_id: str):
    try:
        if Services.leave_group(args['group_id'], user_id):
            close_room(args['group_id'])

        users = Services.get_users([user_id])
        emit('on_leave_group', { 
            'message': f" User {users[0]['username']} has left", 
            'user': users[0]['username']
        }, to=args['group_id'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_find_group(args, user_id: str):
    try:
        group = Services.find_group_by_alias(args['alias'])
        emit('on_find_group', parse_json(group), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())

def on_find_user_groups(user_id: str):
    try:
        groups = Services.find_user_groups(user_id)
        emit('on_find_user_groups', parse_json(groups), to=get_user_session(user_id)['sid'])
    except WeminderAPIError as e:
        emit('on_error', e.json())