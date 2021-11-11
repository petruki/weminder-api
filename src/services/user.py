import bcrypt
from bson.objectid import ObjectId

from .mongodb import db
from errors import BadRequestError

def convert_objectid_to_str(data: dict):
    data['_id'] = str(data['_id'])
    return data

def validate(username: str, password: str):
    """ Validates if username and password are valid """
    
    if not username:
        raise BadRequestError('Username cannot be empty')

    if len(password) < 2:
        raise BadRequestError('Password cannot be less than 2 characters')

def signup(username: str, password: str) -> dict:
    validate(username, password)

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf8'), salt)

    user = {
        'username': username, 
        'password': hashed.decode('utf8'),
        'email': f'{username}@noreply-weminder.ca'
    }
    user_created = db.users.insert_one(user)
    user['_id'] = str(user_created.inserted_id)
    del user['password']
    
    return user

def authenticate(username: str, password: str) -> bool:
    validate(username, password)

    user = db.users.find_one({ 'username': username })
    if user is not None and bcrypt.checkpw(
        password.encode('utf8'), 
        user['password'].encode('utf8')
    ):
        return user

def get_users(user_ids: [str]):
    _in = []
    for u in user_ids:
        _in.append(ObjectId(u))

    users = []
    for data in db.users.find({ '_id': { "$in": _in } }):
        users.append(convert_objectid_to_str({ 
            '_id': data['_id'], 
            'username': data['username'], 
            'email': data['email'] 
        }))

    return users

def get_user_by_id(user_id: str):
    user = db.users.find_one({ '_id': ObjectId(user_id) })
    if user is not None:
        del user['password']
        return convert_objectid_to_str(user)