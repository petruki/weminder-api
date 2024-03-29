import bson
from datetime import datetime

from .mongodb import db
from bson.objectid import ObjectId
from errors import BadRequestError, NotFoundError

def convert_objectid_to_str(data: dict):
    if '_id' in data:
        data['_id'] = str(data['_id'])
    if 'user_id' in data:
        data['user_id'] = str(data['user_id'])
    if 'group_id' in data:
        data['group_id'] = str(data['group_id'])
    return data

def validate(
    group_id = None, 
    title = None, 
    content = None, 
    status = None,
    task_id = None
):
    """ Validates task values """

    if title is not None and len(title) == 0:
        raise BadRequestError('Title cannot be empty')

    if content is not None and len(content) == 0:
        raise BadRequestError('Content cannot be empty')

    if status is not None and len(status) == 0:
        raise BadRequestError('Status cannot be empty')

    if task_id is not None:
        if len(task_id) == 0:
            raise BadRequestError('Task ID cannot be empty')

        if not bson.objectid.ObjectId.is_valid(task_id):
            raise BadRequestError('Invalid Task ID')

    if group_id is not None:
        if len(group_id) == 0:
            raise BadRequestError('Group ID cannot be empty')

        if not bson.objectid.ObjectId.is_valid(group_id):
            raise BadRequestError('Invalid Group ID')

def get_log(message: str, username: str = None):
    time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    return {
        'username': username,
        'message': message,
        'created_at': time
    }

def create_task(user_id: str, group_id: str, title: str, content: str, status: str):
    validate(group_id, title, content, status)

    task = {
        'user_id': ObjectId(user_id),
        'group_id': ObjectId(group_id),
        'title': title,
        'content': content,
        'status': status,
        'log': []
    }

    db.tasks.insert_one(task)
    return convert_objectid_to_str(task)

def get_task(task_id: str):
    validate(task_id=task_id)

    task = db.tasks.find_one({ '_id': ObjectId(task_id) })
    if task is None:
        raise NotFoundError(task_id)

    task = convert_objectid_to_str(task)
    return task

def list_tasks_by_group(group_id: str):
    validate(group_id=group_id)

    tasks = []
    for data in db.tasks.aggregate([
        { '$match': { 'group_id': ObjectId(group_id) } },
        { 
            '$lookup': {
                'from': 'users',
                'let': { 'id': '$user_id' },
                'as': 'created_by',
                'pipeline': [
                    { '$match': { '$expr': { '$eq': [ '$_id', '$$id' ] } } },
                    { '$project': { '_id': 0, 'username': 1 }}
                ],
            }
        },
        { '$unwind': '$created_by' }
    ]):
        tasks.append(convert_objectid_to_str(data))

    return tasks

def update_task(
    current_task: dict,
    task_id: str, 
    title = None, 
    content = None, 
    status = None,
    username = None
):
    validate(task_id=task_id, title=title, content=content)
    
    changes = []
    update = { '$set': {} }
    if title is not None and current_task['title'] != title:
        update['$set']['title'] = title
        changes.append(get_log(f"Title has changed to {title}", username))
    if content is not None and current_task['content'] != content:
        update['$set']['content'] = content
        changes.append(get_log('Content updated', username))
    if status is not None and current_task['status'] != status:
        update['$set']['status'] = status
        changes.append(get_log(f"Status has changed to {status}", username))

    if len(changes) > 0:
        update['$push'] = { 'log': { '$each': changes } }
    
    result = db.tasks.update_one({ '_id': ObjectId(task_id) }, update)
    if result.modified_count == 1:
        task = db.tasks.find_one({ '_id': ObjectId(task_id) })
        return convert_objectid_to_str(task)

def delete_task(task_id: str):
    validate(task_id=task_id)

    result = db.tasks.delete_one({ '_id': ObjectId(task_id) })
    if result.deleted_count == 1:
        return True
    return False

def add_log(task_id: str, content: str, username = None):
    validate(task_id=task_id, content=content)

    update = { '$push': { 'log': get_log(content, username) } }
    result = db.tasks.update_one({ '_id': ObjectId(task_id) }, update)
    if result.modified_count == 1:
        task = db.tasks.find_one({ '_id': ObjectId(task_id) })
        return convert_objectid_to_str(task)