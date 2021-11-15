import os
import json

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from flask_login import LoginManager, login_required
from flask_socketio import SocketIO, emit

import controller as Controller

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

login = LoginManager(app)
socketio = SocketIO(app)

def json_args(func):
    def wrapper(args):
        return func(json.loads(args))
    return wrapper

# Flask Authentication/Connection Routes

@app.route('/', methods=['GET'])
def on_check_flask_handler():
    return { 'status': 'success' }

@app.route('/login', methods=['POST'])
def login_handler():
    return Controller.on_login()

@app.route('/signup', methods=['POST'])
def signup_handler():
    return Controller.on_signup()

# WebSocket Routes

@socketio.on('connect')
def connection_handler():
    return Controller.on_connect(request)

@socketio.on('me')
def me_handler():
    Controller.on_me(request.args.get('auth'))

@socketio.on('logout')
def logout_handler():
    Controller.on_logout(request)

@socketio.on('join_room')
@json_args
def join_group_room_handler(args):
    Controller.on_join_group_room(args)
    
@socketio.on('check')
@json_args
def on_check_handler(args):
    Controller.on_check(args)

# Group Routes

@socketio.on('create_group')
@json_args
def create_group_handler(args):
    Controller.on_create_group(args, request.args.get('auth'))

@socketio.on('update_group')
@json_args
def update_group_handler(args):
    Controller.on_update_group(args)

@socketio.on('find_group')
@json_args
def find_group_handler(args):
    Controller.on_find_group(args, request.args.get('auth'))

@socketio.on('find_user_groups')
def find_user_groups_handler(args):
    Controller.on_find_user_groups(request.args.get('auth'))

@socketio.on('find_group_users')
@json_args
def find_group_users_handler(args):
    Controller.on_find_group_users(args, request.args.get('auth'))

@socketio.on('join_group')
@json_args
def join_group_handler(args):
    Controller.on_join_group(args, request.args.get('auth'))

@socketio.on('leave_group')
@json_args
def leave_group_handler(args):
    Controller.on_leave_group(args, request.args.get('auth'))

# Task Routes

@socketio.on('create_task')
@json_args
def create_task_handler(args):
    Controller.on_create_task(args, request.args.get('auth'))

@socketio.on('get_task')
@json_args
def get_task_handler(args):
    Controller.on_get_task(args, request.args.get('auth'))

@socketio.on('list_tasks')
@json_args
def list_task_handler(args):
    Controller.on_list_tasks(args, request.args.get('auth'))

@socketio.on('update_task')
@json_args
def update_task_handler(args):
    Controller.on_update_task(args, request.args.get('auth'))

@socketio.on('delete_task')
@json_args
def delete_task_handler(args):
    Controller.on_delete_task(args)

@socketio.on('add_log')
@json_args
def add_log_handler(args):
    Controller.on_add_log(args, request.args.get('auth'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)