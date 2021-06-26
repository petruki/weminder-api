from flask import request, abort
from flask_login import login_user, logout_user
from flask_socketio import emit, join_room, leave_room, disconnect

from model import User
from errors import WeminderAPIError
import services as Services

parse_json = Services.parse_json
connected_users = []

def get_user_session(user_id: str) -> dict:
    """ Return dictionary containing 'user_id' and 'sid' """

    for data in connected_users:
        if data['user_id'] == user_id:
            return data

def on_connect(current_user):
    if not current_user.is_anonymous:
        # Remove user if connected
        existing_user = get_user_session(current_user.id)
        if existing_user:
            disconnect(existing_user['sid'])
            connected_users.remove(existing_user)

        # Save session info
        connected_users.append({
            'user_id': current_user.id,
            'sid': request.sid
        })

        return emit('connected', { 'id': current_user.id })
    return False

def on_join_group_room(args):
    group_room = args['group_id']
    join_room(group_room)

def on_leave_group_room(args):
    group_room = args['group_id']
    leave_room(group_room)

def on_login():
    username = request.form['username']
    password = request.form['password']

    try:
        user = Services.authenticate(username, password)
        if not user:
            abort(401)

        login_user(User(user['_id']))
        return ''
    except WeminderAPIError as e:
        return parse_json(e.json()), 400

def on_signup():
    username = request.form['username']
    password = request.form['password']

    try:
        user = Services.signup(username, password)
        if user is None:
            abort(500)
        
        return parse_json(user), 201
    except WeminderAPIError as e:
        return parse_json(e.json()), 400

def on_logout():
    logout_user()
    return ''