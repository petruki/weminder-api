from flask import request, abort
from flask_socketio import emit, join_room, leave_room, disconnect

from errors import WeminderAPIError
import services as Services

parse_json = Services.parse_json
connected_users = []

def get_user_session(user_id: str) -> dict:
    """ Return dictionary containing 'user_id' and 'sid' """

    for data in connected_users:
        if data['user_id'] == user_id:
            return data

def on_connect(request):
    user_id = request.args.get('auth')

    # Remove user if connected
    existing_user = get_user_session(user_id)
    if existing_user:
        disconnect(existing_user['sid'])
        connected_users.remove(existing_user)

    # Save session info
    connected_users.append({
        'user_id': user_id,
        'sid': request.sid
    })

    return emit('connected', { 'id': user_id })

def on_join_group_room(args, user_id: str):
    group_room = args['group_id']
    join_room(group_room, sid=get_user_session(user_id)['sid'])

def on_leave_group_room(args, user_id):
    group_room = args['group_id']
    leave_room(group_room, sid=get_user_session(user_id)['sid'])

def on_login():
    username = request.get_json()['username']
    password = request.get_json()['password']

    try:
        user = Services.authenticate(username, password)
        if not user:
            abort(401)
        
        return {
            '_id': user['_id'].__str__(),
            'username': user['username'],
            'email': user['email']
        }
    except WeminderAPIError as e:
        return parse_json(e.json()), 400

def on_signup():
    username = request.get_json()['username']
    password = request.get_json()['password']

    try:
        user = Services.signup(username, password)
        if user is None:
            abort(500)
        
        return parse_json(user), 201
    except WeminderAPIError as e:
        return parse_json(e.json()), 400

def on_me(user_id):
    user = Services.get_user_by_id(user_id)
    if user is not None:
        emit('on_me', parse_json(user), to=get_user_session(user_id)['sid'])

def on_logout(user_id: str):
    existing_user = get_user_session(user_id)
    if existing_user:
        disconnect(existing_user['sid'])
        connected_users.remove(existing_user)