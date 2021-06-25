from bson.objectid import ObjectId

from src.services.mongodb import db

def tear_down_group():
    db.groups.delete_many({})

def setup_db_group():
    db.groups.insert_one({
        'name': 'Fixture 1', 
        'alias': 'FIXTURE1',
        'users': []
    })

def add_user_to_group(group_id: str, username: str):
    user = db.users.find_one({ 'username': username })
    db.groups.update_one({ 
        '_id': ObjectId(group_id)}, {
            '$push': { 'users': user['_id'] } 
        }
    )