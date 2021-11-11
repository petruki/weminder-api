import bson

from .mongodb import db

from bson.objectid import ObjectId

from errors import NotFoundError, BadRequestError, InternalErrorError

def convert_objectid_to_str(data: dict):
    if '_id' in data:
        data['_id'] = str(data['_id'])
    return data

def validate(
    name = None, 
    alias = None, 
    user_id = None,
    group_id = None
):
    """ Validates group values """

    if name is not None and len(name) == 0:
        raise BadRequestError('Name cannot be empty')

    if alias is not None and len(alias) == 0:
        raise BadRequestError('Alias cannot be empty')

    if user_id is not None:
        if len(user_id) == 0:
            raise BadRequestError('User ID cannot be empty')

        if not bson.objectid.ObjectId.is_valid(user_id):
            raise BadRequestError('Invalid User ID')

    if group_id is not None:
        if len(group_id) == 0:
            raise BadRequestError('Group ID cannot be empty')

        if not bson.objectid.ObjectId.is_valid(group_id):
            raise BadRequestError('Invalid Group ID')

def create_group(name: str, alias: str, user_id: str):
    validate(name, alias, user_id)

    group = {
        'name': name,
        'alias': alias,
        'users': [user_id]
    }

    db.groups.insert_one(group)
    return convert_objectid_to_str(group)

def update_group(group_id: str, name: str, alias: str):
    validate(group_id=group_id, name=name, alias=alias)

    update = { '$set': {} }
    if name is not None:
        update['$set']['name'] = name
    if alias is not None:
        update['$set']['alias'] = alias

    result = db.groups.update_one({ '_id': ObjectId(group_id) }, update)

    if result.modified_count == 1:
        group = db.groups.find_one({ '_id': ObjectId(group_id) })
        return convert_objectid_to_str(group)

def join_group(group_id: str, user_id: str):
    result = db.groups.update_one({ 
        '_id': ObjectId(group_id)}, {
            '$push': { 'users': user_id } 
        }
    )

    if result.modified_count != 1:
        raise InternalErrorError(
            f"Not possible to join Group {group_id} as User {user_id}")
            
    return convert_objectid_to_str(db.groups.find_one({ '_id': ObjectId(group_id) }))

def leave_group(group_id: str, user_id):
    validate(user_id=user_id, group_id=group_id)

    result = db.groups.update_one({ 
        '_id': ObjectId(group_id)}, {
            '$pull': { 'users': user_id } 
        }
    )

    if result.modified_count != 1:
        raise InternalErrorError(
            f"Not possible to leave Group {group_id} as User {user_id}")

    group = convert_objectid_to_str(db.groups.find_one({ '_id': ObjectId(group_id) }))
    if len(group['users']) == 0:
        db.groups.delete_one({ '_id': ObjectId(group_id) })
        return True, group

    return False, group

def find_group_by_alias(alias: str):
    validate(alias=alias)

    group = db.groups.find_one({ 'alias': alias })

    if group is None:
        raise NotFoundError(alias)

    return convert_objectid_to_str(group)

def find_group_by_id(group_id: str):
    validate(group_id=group_id)

    group = db.groups.find_one({ '_id': ObjectId(group_id) })

    if group is None:
        raise NotFoundError(alias)

    return convert_objectid_to_str(group)

def find_user_groups(user_id: str):
    validate(user_id=user_id)

    groups = []
    for data in db.groups.find({ 'users': [user_id] }):
        groups.append(convert_objectid_to_str(data))
        
    if len(groups) == 0:
        return []

    return groups

def find_group_users(group_id: str):
    validate(group_id=group_id)

    group = db.groups.find_one({ '_id': ObjectId(group_id) })

    if group is None:
        raise NotFoundError(group_id)

    return group['users']