from .mongodb import db

from bson.objectid import ObjectId

from errors import NotFoundError, InternalErrorError

def group_input(name: str, alias: str, user_id: str):
    """ Validates group values """
    pass

def create_group(name: str, alias: str, user_id: str):
    group_input(name, alias, user_id)

    group = {
        'name': name,
        'alias': alias,
        'users': [user_id]
    }

    db.groups.insert_one(group)
    return group

def join_group(group_id: str, user_id: str):
    result = db.groups.update_one({ 
        '_id': ObjectId(group_id)}, {
            '$push': { 'users': user_id } 
        }
    )

    if result.modified_count != 1:
        raise InternalErrorError(
            f"Not possible to join Group {group_id} as User {user_id}")

def leave_group(group_id: str, user_id):
    result = db.groups.update_one({ 
        '_id': ObjectId(group_id)}, {
            '$pull': { 'users': user_id } 
        }
    )

    if result.modified_count != 1:
        raise InternalErrorError(
            f"Not possible to leave Group {group_id} as User {user_id}")

    group = db.groups.find_one({ '_id': ObjectId(group_id) })
    if len(group['users']) == 0:
        db.groups.delete_one({ '_id': ObjectId(group_id) })

def find_group_by_alias(alias: str):
    group = db.groups.find_one({ 'alias': alias })

    if group is None:
        raise NotFoundError(alias)

    return group

def find_user_groups(user_id: str):
    groups = []
    for data in db.groups.find({ 'users': [user_id] }):
        groups.append(data)
        
    if len(groups) == 0:
        return []

    return groups
