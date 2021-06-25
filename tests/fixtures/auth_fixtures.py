import bcrypt

from src.services.mongodb import db

def tear_down_auth():
    db.users.delete_many({})

def setup_db_auth():
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b'123', salt)
    db.users.insert_one({
        'username': 'roger', 
        'password': hashed.decode('utf8'),
        'email': 'roger@noreply-weminder.ca'
    })

    db.users.insert_one({
        'username': 'anna', 
        'password': hashed.decode('utf8'),
        'email': 'anna@noreply-weminder.ca'
    })