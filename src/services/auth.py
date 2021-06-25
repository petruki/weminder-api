import bcrypt

from .mongodb import db
from errors import BadRequestError

def user_input(username: str, password: str):
    """ Validates if username and password are valid """
    
    if not username:
        raise BadRequestError('Username cannot be empty')

    if len(password) < 2:
        raise BadRequestError('Password cannot be less than 2 characters')

def signup(username: str, password: str) -> dict:
    user_input(username, password)

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)

    user = {
        'username': username, 
        'password': hashed.decode('utf8'),
        'email': f'{username}@noreply-weminder.ca'
    }
    db.users.insert_one(user)
    del user['password']
    return user

def authenticate(username: str, password: str) -> bool:
    user_input(username, password)

    user = db.users.find_one({ 'username': username })
    if user is not None and bcrypt.checkpw(
        password.encode('utf8'), 
        user['password'].encode('utf8')
    ):
        return user