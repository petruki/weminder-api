from flask_socketio import emit

def on_check(args):
    emit('on_check', { 'message': f"All good {args['user']}" })