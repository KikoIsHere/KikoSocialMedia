from flask_socketio import send, join_room, emit
from flask_login import current_user
from flask import request
from . import db, socketio
from .models import User

@socketio.on('private message', namespace='/message/')
def join(msg):
    join_room(request.sid)
    room = request.sid
    emit("my response",{ "data" : msg['data'] },room=room)
