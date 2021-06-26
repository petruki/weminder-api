import bcrypt

from src.services.mongodb import db

def tear_down_user():
    db.users.delete_many({})

def setup_db_user():
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b'123', salt)

    user_roger = {
        'username': 'roger', 
        'password': hashed.decode('utf8'),
        'email': 'roger@noreply-weminder.ca'
    }

    user_anna = {
        'username': 'anna', 
        'password': hashed.decode('utf8'),
        'email': 'anna@noreply-weminder.ca'
    }

    db.users.insert_one(user_roger)
    db.users.insert_one(user_anna)

    return (user_roger, user_anna)