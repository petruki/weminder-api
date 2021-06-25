import os

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_login import LoginManager, login_required, current_user
from flask_socketio import SocketIO, emit

import controller as Controller
from model import User

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

login = LoginManager(app)
socketio = SocketIO(app)

# Authentication/Connection Routes

@app.route('/login', methods=['POST'])
def login_handler():
    return Controller.on_login()
    # return on_login()

@app.route('/signup', methods=['POST'])
def signup_handler():
    return Controller.on_signup()

@app.route('/logout', methods=['POST'])
@login_required
def logout_handler():
    return Controller.on_logout()

@login.user_loader
def user_loader(id):
    return User(id)

@socketio.on('connect')
def connection_handler():
    return Controller.on_connect(current_user)

@socketio.on('check')
def on_check_handler(args):
    Controller.on_check(args)

# Group Routes

@socketio.on('create_group')
def create_group_handler(args):
    Controller.on_create_group(args, current_user.id)

@socketio.on('find_group')
def find_group_handler(args):
    Controller.on_find_group(args)

@socketio.on('find_user_groups')
def find_user_groups_handler(args):
    Controller.on_find_user_groups(current_user.id)

@socketio.on('join_group')
def join_group_handler(args):
    Controller.on_join_group(args, current_user.id)

@socketio.on('leave_group')
def leave_group_handler(args):
    Controller.on_leave_group(args, current_user.id)

# Task Routes

@socketio.on('create_task')
def create_task_handler(args):
    Controller.on_create_task(args, current_user.id)

if __name__ == '__main__':
    socketio.run(app)